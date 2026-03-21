
from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine
from unilog.engine.model import Model, World
class SMTModel(Model):
    def __init__(self): self.w=World(0)
    def worlds(self): return {self.w}
    def valuation(self,w,a,args): return True
    def accessibility(self,w,m,a=None): return set()
    def domain(self): return {0}
    def interpret(self,t,s): return getattr(t,'value', getattr(t,'name',None))
    def probability(self,w,e): return 1.0 if w in e else 0.0
    def preference(self,w,w1,w2): return False
    def smt_background(self):
        yield ('declare', ('p',1))
phi = UniLangParser().parse_string('forall X. p(X) -> p(X)')
print('SMT validity (Z3 or fallback):', InferenceEngine.get_instance().evaluate(phi, SMTModel()))
