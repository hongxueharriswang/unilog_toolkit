
from antlr4 import InputStream, CommonTokenStream
from .UniLangLexer import UniLangLexer
from .UniLangParser import UniLangParser as AntlrParser
from .error_listener import ThrowingErrorListener
from .errors import UniLangSyntaxError
from ..ast import *

class ASTBuilder:
    def build(self, text: str):
        stream = InputStream(text)
        lexer = UniLangLexer(stream)
        tokens = CommonTokenStream(lexer)
        parser = AntlrParser(tokens)
        parser.removeErrorListeners(); parser.addErrorListener(ThrowingErrorListener())
        tree = parser.start()
        formulas=[]
        for i,ch in enumerate(tree.children or []):
            if hasattr(ch,'getRuleIndex') and parser.ruleNames[ch.getRuleIndex()]=='formula':
                formulas.append(self._visit_any(ch))
        if not formulas:
            tokens.seek(0); parser = AntlrParser(tokens)
            parser.removeErrorListeners(); parser.addErrorListener(ThrowingErrorListener())
            fctx = parser.formula(); return self._visit_any(fctx)
        if len(formulas)==1: return formulas[0]
        res = formulas[0]
        for f in formulas[1:]: res = AndFormula(res,f)
        return res

    # Generic pattern-based visitor (keeps implementation compact)
    def _visit_any(self, ctx):
        # Parentheses
        if ctx.getChildCount()==3 and ctx.getChild(0).getText()=='(' and ctx.getChild(2).getText()==')':
            return self._visit_any(ctx.getChild(1))
        # true/false
        if ctx.getText()=='true': return Atom('true',[])
        if ctx.getText()=='false': return Atom('false',[])
        # Quantifiers
        if ctx.getChildCount()>=5 and ctx.getChild(0).getText() in ('forall','exists'):
            q = ctx.getChild(0).getText(); var = ctx.getChild(1).getText(); sort=''
            i=2
            if ctx.getChild(2).getText()==':': sort=ctx.getChild(3).getText(); i=5
            else: i=3
            body = self._visit_any(ctx.getChild(i))
            return ForallFormula(var, sort, body) if q=='forall' else ExistsFormula(var, sort, body)
        # IFF
        for i in range(1, ctx.getChildCount()-1):
            if ctx.getChild(i).getText()=="<->":
                return IffFormula(self._visit_any(ctx.getChild(0)), self._visit_any(ctx.getChild(i+1)))
        # -> and =>
        for i in range(1, ctx.getChildCount()-1):
            if ctx.getChild(i).getText() in ('->','=>'):
                left=self._visit_any(ctx.getChild(0)); right=self._visit_any(ctx.getChild(i+1))
                return ImpliesFormula(left,right) if ctx.getChild(i).getText()=='->' else DefaultImplies(left,right)
        # Preference φ < ψ
        for i in range(1, ctx.getChildCount()-1):
            if ctx.getChild(i).getText()=='<':
                return Preference(self._visit_any(ctx.getChild(0)), self._visit_any(ctx.getChild(i+1)))
        # AND (&G/&L/&P)
        for i in range(1, ctx.getChildCount()-1):
            t=ctx.getChild(i).getText()
            if t in ('and','&G','&L','&P'):
                l=self._visit_any(ctx.getChild(0)); r=self._visit_any(ctx.getChild(i+1))
                return AndFormula(l,r) if t=='and' else FuzzyAnd(l,r,t[1])
        # OR (|G/|L/|P)
        for i in range(1, ctx.getChildCount()-1):
            t=ctx.getChild(i).getText()
            if t in ('or','|G','|L','|P'):
                l=self._visit_any(ctx.getChild(0)); r=self._visit_any(ctx.getChild(i+1))
                return OrFormula(l,r) if t=='or' else FuzzyOr(l,r,t[1])
        # NOT, ~G, ~L, ~P
        if ctx.getChildCount()>=2 and ctx.getChild(0).getText() in ('not','~G','~L','~P'):
            op=ctx.getChild(0).getText(); sub=self._visit_any(ctx.getChild(1))
            return NotFormula(sub) if op=='not' else FuzzyNot(sub, op[1])
        # Modal/temporal/dynamic
        if ctx.getChildCount()>=2:
            t0=ctx.getChild(0).getText()
            if t0=='box':
                i=1; ag=None
                if ctx.getChild(1).getText()=='[': ag=ctx.getChild(2).getText(); i=5
                return BoxModal('box', ag, self._visit_any(ctx.getChild(i)))
            if t0=='diamond':
                i=1; ag=None
                if ctx.getChild(1).getText()=='[': ag=ctx.getChild(2).getText(); i=5
                return DiamondModal('diamond', ag, self._visit_any(ctx.getChild(i)))
            if t0=='K':
                ag=ctx.getChild(2).getText(); return KFormula(ag, self._visit_any(ctx.getChild(4)))
            if t0=='B':
                ag=ctx.getChild(2).getText(); return BFormula(ag, self._visit_any(ctx.getChild(4)))
            if t0=='O': return OFormula(self._visit_any(ctx.getChild(1)))
            if t0=='P' and ctx.getChild(1).getText()!='(': return PFormula(self._visit_any(ctx.getChild(1)))
            if t0=='G':
                i=1; bound=None
                if ctx.getChildCount()>=4 and ctx.getChild(1).getText().startswith('_['):
                    txt=ctx.getChild(1).getText()[2:-1]; l,u=txt.split(','); bound=(float(l),float(u)); i=2
                return GFormula(self._visit_any(ctx.getChild(i)), bound)
            if t0=='F':
                i=1; bound=None
                if ctx.getChildCount()>=4 and ctx.getChild(1).getText().startswith('_['):
                    txt=ctx.getChild(1).getText()[2:-1]; l,u=txt.split(','); bound=(float(l),float(u)); i=2
                return FFormula(self._visit_any(ctx.getChild(i)), bound)
            if t0=='X': return XFormula(self._visit_any(ctx.getChild(1)))
            if t0=='[':
                return BoxAction(self.visit_action(ctx.getChild(1)), self._visit_any(ctx.getChild(3)))
            if t0=='<':
                return DiamondAction(self.visit_action(ctx.getChild(1)), self._visit_any(ctx.getChild(3)))
            if t0 in ('P_>=','P_<=','P_='):
                th=float(ctx.getChild(1).getText()); sub=self._visit_any(ctx.getChild(3))
                return ProbGeq(th,sub) if t0=='P_>=' else (ProbLeq(th,sub) if t0=='P_<=' else ProbEq(th,sub))
            if t0=='E' and ctx.getChild(1).getText()=='[':
                return ExpectedValue(self.visit_term(ctx.getChild(2)))
            if t0=='Opt': return Optimal(self._visit_any(ctx.getChild(2)))
        # Description logic application handled by grammar; fall back to atom if function-like
        try:
            first=ctx.getChild(0).getText()
            if first not in ('true','false','(') and ctx.getChild(1).getText()=='(':
                args=[]; i=2
                while i<ctx.getChildCount()-1:
                    if ctx.getChild(i).getText()!=',': args.append(self.visit_term(ctx.getChild(i)))
                    i+=1
                return Atom(first, args)
        except Exception:
            pass
        raise UniLangSyntaxError(f"Unsupported or unrecognized fragment: {ctx.getText()}")

    def visit_action(self, ctx):
        if ctx.getChildCount()==1: return AtomicAction(ctx.getChild(0).getText())
        if ctx.getChildCount()==3 and ctx.getChild(1).getText()==';':
            return SequenceAction(self.visit_action(ctx.getChild(0)), self.visit_action(ctx.getChild(2)))
        if ctx.getChildCount()==3 and ctx.getChild(1).getText()=='|':
            return ChoiceAction(self.visit_action(ctx.getChild(0)), self.visit_action(ctx.getChild(2)))
        if ctx.getChildCount()==2 and ctx.getChild(1).getText()=='*':
            return StarAction(self.visit_action(ctx.getChild(0)))
        if ctx.getChildCount()==2 and ctx.getChild(0).getText()=='?':
            return TestAction(self._visit_any(ctx.getChild(1)))
        if ctx.getChildCount()==3 and ctx.getChild(0).getText()=='(':
            return self.visit_action(ctx.getChild(1))
        raise UniLangSyntaxError(f"Unsupported action: {ctx.getText()}")

    def visit_term(self, ctx):
        if ctx.getChildCount()==1:
            txt=ctx.getChild(0).getText()
            if txt.startswith('"') and txt.endswith('"'): return Constant(txt[1:-1])
            if txt.replace('.','',1).isdigit(): return Constant(float(txt) if '.' in txt else int(txt))
            return Variable(txt) if txt and txt[0].isupper() else Constant(txt)
        if ctx.getChildCount()>=3 and ctx.getChild(1).getText()=='(':
            name=ctx.getChild(0).getText(); args=[]
            for i in range(2, ctx.getChildCount()-1):
                if ctx.getChild(i).getText()!=',': args.append(self.visit_term(ctx.getChild(i)))
            return Function(name,args)
        raise UniLangSyntaxError(f"Unsupported term: {ctx.getText()}")

class UniLangParser:
    def __init__(self): self.builder=ASTBuilder()
    def parse_string(self, text: str):
        try: return self.builder.build(text)
        except Exception as e:
            if isinstance(e, UniLangSyntaxError): raise
            raise UniLangSyntaxError(str(e))
    def parse_file(self, path: str):
        with open(path,'r',encoding='utf-8') as f: return self.parse_string(f.read())
