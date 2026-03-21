
import unittest
from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine
from unilog.engine.model import Model, World
class M(Model):
    def __init__(self): self.w1,self.w2=World('w1'),World('w2')
    def worlds(self): return {self.w1,self.w2}
    def valuation(self,w,a,args): return a=='p' and w==self.w1
    def accessibility(self,w,m,a=None): return set()
    def domain(self): return set()
    def interpret(self,t,s): return getattr(t,'value', getattr(t,'name',None))
    def probability(self,w,e): return len(e)/2.0
    def preference(self,w,w1,w2): return False
class TestProb(unittest.TestCase):
    def test_geq(self):
        f = UniLangParser().parse_string('P_>= 0.5 (p())')
        self.assertTrue(InferenceEngine.get_instance().evaluate(f, M()))
if __name__=='__main__': unittest.main()
