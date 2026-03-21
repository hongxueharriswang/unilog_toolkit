
from typing import Dict, Any
from .model import Model, World
from ..ast import *
from .adapters.smt import SMTLibEncoder, Z3Adapter
from .adapters.prism import PrismAdapter
from .adapters.clingo import ClingoAdapter

class DefaultLogicSolver:
    def supports(self, f: Formula)->bool: return isinstance(f, DefaultImplies)
    def evaluate(self, f: DefaultImplies, m: Model, w: World, s: Dict[str,Any]):
        asp = ClingoAdapter()
        if asp.is_available():
            prog = self._encode_default(f)
            ok, out = asp.run_asp(prog)
            return 'holds' in out
        from .solvers import ClassicalSolver
        return ClassicalSolver().evaluate(ImpliesFormula(f.antecedent, f.consequent), m, w, s)
    def _encode_default(self, f: DefaultImplies)->str:
        return ("% auto-generated from UniLang default
"
                "antecedent.
"
                "consequent :- antecedent, not neg_consequent.
"
                "holds :- consequent.
")

class SMTSolver:
    def supports(self, f: Formula)->bool: return isinstance(f, (ForallFormula, ExistsFormula))
    def evaluate(self, f: Formula, m: Model, w: World, s: Dict[str,Any]):
        z3 = Z3Adapter()
        if not z3.is_available():
            from .solvers import ClassicalSolver
            return ClassicalSolver().evaluate(f,m,w,s)
        enc = SMTLibEncoder()
        ctx = getattr(m,'smt_background',None)
        if callable(ctx):
            for decl, body in ctx():
                if decl=='assert': enc.assert_clause(body)
                elif decl=='declare': name,arity=body; enc.declare_pred(name,arity)
        phi = self._enc(f); enc.assert_clause(f"(not {phi})")
        ok, out = z3.run_smt(enc.check_sat())
        if not ok:
            from .solvers import ClassicalSolver
            return ClassicalSolver().evaluate(f,m,w,s)
        return 'unsat' in out
    def _enc(self, f: Formula)->str:
        if isinstance(f, Atom):
            if f.args: return f"({f.name} {' '.join(['0']*len(f.args))})"
            return f.name
        if isinstance(f, AndFormula): return f"(and {self._enc(f.left)} {self._enc(f.right)})"
        if isinstance(f, OrFormula): return f"(or {self._enc(f.left)} {self._enc(f.right)})"
        if isinstance(f, NotFormula): return f"(not {self._enc(f.sub)})"
        if isinstance(f, ImpliesFormula): return f"(=> {self._enc(f.left)} {self._enc(f.right)})"
        if isinstance(f, IffFormula):
            a=self._enc(f.left); b=self._enc(f.right); return f"(and (=> {a} {b}) (=> {b} {a}))"
        if isinstance(f, ForallFormula): return f"(forall (({f.var} Int)) {self._enc(f.body)})"
        if isinstance(f, ExistsFormula): return f"(exists (({f.var} Int)) {self._enc(f.body)})"
        return 'true'

class ProbabilisticSolver:
    def supports(self, f: Formula)->bool: return isinstance(f, (ProbGeq, ProbLeq, ProbEq))
    def evaluate(self, f: Formula, m: Model, w: World, s: Dict[str,Any]):
        adapter = PrismAdapter()
        if adapter.is_available():
            gen = getattr(m,'prism_model',None)
            if callable(gen):
                mtext, ptext = gen(f)
                ok, out = adapter.run_prism(mtext, ptext)
                if ok:
                    import re
                    match = re.search(r"([01]?\.\d+)", out)
                    if match:
                        prob = float(match.group(1))
                        return self._cmp(prob, f)
        # fallback: compute P via model.probability over event set
        from .inference import InferenceEngine
        holds=set()
        for ww in m.worlds():
            if InferenceEngine.get_instance().evaluate(getattr(f,'sub', Atom('true',[])), m, ww, s):
                holds.add(ww)
        p = m.probability(w, holds)
        return self._cmp(p, f)
    def _cmp(self, p: float, f: Formula)->bool:
        if isinstance(f, ProbGeq): return p >= f.threshold
        if isinstance(f, ProbLeq): return p <= f.threshold
        if isinstance(f, ProbEq): return abs(p - f.threshold) < 1e-9
        return False
