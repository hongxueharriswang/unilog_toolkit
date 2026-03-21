
from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine
from unilog.engine.model import Model, World
class ProbModel(Model):
    def __init__(self): self.w1,self.w2=World('w1'),World('w2')
    def worlds(self): return {self.w1,self.w2}
    def valuation(self,w,a,args): return a=='p' and w==self.w1
    def accessibility(self,w,m,a=None): return set()
    def domain(self): return set()
    def interpret(self,t,s): return getattr(t,'value', getattr(t,'name',None))
    def probability(self,w,e): return len(e)/2.0
    def preference(self,w,w1,w2): return False
phi = UniLangParser().parse_string('P_>= 0.6 (p())')
print('Probabilistic check:', InferenceEngine.get_instance().evaluate(phi, ProbModel()))
