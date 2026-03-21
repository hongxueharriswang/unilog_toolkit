
from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine
from unilog.engine.model import Model, World
class M(Model):
    def __init__(self): self.w=World('w')
    def worlds(self): return {self.w}
    def valuation(self,w,a,args): return False
    def accessibility(self,w,m,a=None): return set()
    def domain(self): return set()
    def interpret(self,t,s): return getattr(t,'value', getattr(t,'name',None))
    def probability(self,w,e): return 1.0 if w in e else 0.0
    def preference(self,w,w1,w2): return False
phi = UniLangParser().parse_string('phi() => psi()')
print('Default implication (clingo or fallback):', InferenceEngine.get_instance().evaluate(phi, M()))
