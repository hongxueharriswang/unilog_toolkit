
from abc import ABC, abstractmethod
from ..ast import *
from .model import Model, World
from typing import Dict, Any, Set
class Solver(ABC):
    @abstractmethod
    def supports(self, formula: Formula)->bool: ...
    @abstractmethod
    def evaluate(self, formula: Formula, model: Model, world: World, assignment: Dict[str,Any]): ...
class ClassicalSolver(Solver):
    def supports(self, f):
        return isinstance(f,(Atom,AndFormula,OrFormula,NotFormula,ImpliesFormula,IffFormula,ForallFormula,ExistsFormula))
    def evaluate(self, f, m, w, s):
        if isinstance(f, Atom):
            args=[m.interpret(a,s) for a in f.args]
            return m.valuation(w,f.name,tuple(args))
        if isinstance(f, AndFormula): return self.evaluate(f.left,m,w,s) and self.evaluate(f.right,m,w,s)
        if isinstance(f, OrFormula): return self.evaluate(f.left,m,w,s) or self.evaluate(f.right,m,w,s)
        if isinstance(f, NotFormula): return not self.evaluate(f.sub,m,w,s)
        if isinstance(f, ImpliesFormula): return (not self.evaluate(f.left,m,w,s)) or self.evaluate(f.right,m,w,s)
        if isinstance(f, IffFormula):
            l=self.evaluate(f.left,m,w,s); r=self.evaluate(f.right,m,w,s); return l==r
        if isinstance(f, ForallFormula):
            for d in m.domain():
                ns=dict(s); ns[f.var]=d
                if not self.evaluate(f.body,m,w,ns): return False
            return True
        if isinstance(f, ExistsFormula):
            for d in m.domain():
                ns=dict(s); ns[f.var]=d
                if self.evaluate(f.body,m,w,ns): return True
            return False
        raise NotImplementedError
class ModalSolver(Solver):
    def supports(self,f):
        return isinstance(f,(BoxModal,DiamondModal,KFormula,BFormula,OFormula,PFormula,FModal))
    def evaluate(self,f,m,w,s):
        from .inference import InferenceEngine
        if isinstance(f,(BoxModal,KFormula,BFormula,OFormula,FModal)):
            rel=getattr(f,'modality','box'); ag=getattr(f,'agent',None)
            return all(InferenceEngine.get_instance().evaluate(f.sub,m,ww,s) for ww in m.accessibility(w,rel,ag))
        if isinstance(f,(DiamondModal,PFormula)):
            rel=getattr(f,'modality','diamond'); ag=getattr(f,'agent',None)
            return any(InferenceEngine.get_instance().evaluate(f.sub,m,ww,s) for ww in m.accessibility(w,rel,ag))
        raise NotImplementedError
class TemporalSolver(Solver):
    MAX_DEPTH=10
    def supports(self,f): return isinstance(f,(GFormula,FFormula,XFormula,UntilFormula,ReleaseFormula,AFormula,EFormula))
    def evaluate(self,f,m,w,s):
        from .inference import InferenceEngine
        def nxt(u): return m.accessibility(u,'T') or set()
        def eval_at(u, g): return InferenceEngine.get_instance().evaluate(g,m,u,s)
        if isinstance(f,XFormula): return any(eval_at(u,f.sub) for u in nxt(w))
        if isinstance(f,GFormula):
            l,u = (0,int(self.MAX_DEPTH)) if not f.bound else (int(f.bound[0]), int(f.bound[1]))
            frontier={w}
            for _ in range(u+1):
                if not all(eval_at(x,f.sub) for x in frontier): return False
                nn=set()
                for x in frontier: nn|=nxt(x)
                if not nn: break
                frontier=nn
            return True
        if isinstance(f,FFormula):
            l,u = (0,int(self.MAX_DEPTH)) if not f.bound else (int(f.bound[0]), int(f.bound[1]))
            frontier={w}
            for _ in range(u+1):
                if any(eval_at(x,f.sub) for x in frontier): return True
                nn=set()
                for x in frontier: nn|=nxt(x)
                if not nn: break
                frontier=nn
            return False
        if isinstance(f,UntilFormula):
            u = int(self.MAX_DEPTH) if not f.bound else int(f.bound[1])
            frontier={w}
            for _ in range(u+1):
                if any(eval_at(x,f.right) for x in frontier): return True
                if not all(eval_at(x,f.left) for x in frontier): return False
                nn=set()
                for x in frontier: nn|=nxt(x)
                if not nn: break
                frontier=nn
            return False
        if isinstance(f,ReleaseFormula):
            u = int(self.MAX_DEPTH) if not f.bound else int(f.bound[1])
            frontier={w}
            for _ in range(u+1):
                if all(eval_at(x,f.right) for x in frontier):
                    if any(eval_at(x,f.left) for x in frontier): return True
                    nn=set()
                    for x in frontier: nn|=nxt(x)
                    if not nn: return True
                    frontier=nn
                else: return False
            return True
        if isinstance(f,AFormula): return self.evaluate(GFormula(f.sub),m,w,s)
        if isinstance(f,EFormula): return self.evaluate(FFormula(f.sub),m,w,s)
        return True
class FuzzySolver(Solver):
    def supports(self,f): return isinstance(f,(FuzzyAnd,FuzzyOr,FuzzyNot,GradedTruth))
    def evaluate(self,f,m,w,s):
        from .inference import InferenceEngine
        def tv(v): return float(v) if isinstance(v,(int,float)) else (1.0 if v else 0.0)
        if isinstance(f,FuzzyAnd):
            l=tv(InferenceEngine.get_instance().evaluate(f.left,m,w,s)); r=tv(InferenceEngine.get_instance().evaluate(f.right,m,w,s))
            return min(l,r) if f.norm=='G' else (max(0.0,l+r-1.0) if f.norm=='L' else l*r)
        if isinstance(f,FuzzyOr):
            l=tv(InferenceEngine.get_instance().evaluate(f.left,m,w,s)); r=tv(InferenceEngine.get_instance().evaluate(f.right,m,w,s))
            return max(l,r) if f.norm=='G' else (min(1.0,l+r) if f.norm=='L' else (l + r - l*r))
        if isinstance(f,FuzzyNot):
            return 1.0 - tv(InferenceEngine.get_instance().evaluate(f.sub,m,w,s))
        if isinstance(f,GradedTruth):
            return tv(InferenceEngine.get_instance().evaluate(f.sub,m,w,s)) >= f.threshold
        raise NotImplementedError
