"""
K[agent] p
K[agent] q
"""

from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine
from unilog.engine.model import Model, World

class EpistemicModel(Model):
    def __init__(self):
        self.w0 = World(0)
        self.w1 = World(1)
        # agent considers both worlds possible
        self._access = {
            (self.w0, 'K', 'agent'): {self.w0, self.w1},
            (self.w1, 'K', 'agent'): {self.w0, self.w1},
        }

    def worlds(self): return {self.w0, self.w1}

    def valuation(self, world, atom, args):
        if world == self.w0:
            return atom == 'p' and args == ()
        else:  # world == self.w1
            return atom == 'q' and args == ()

    def accessibility(self, world, modality, agent=None):
        return self._access.get((world, modality, agent), set())

    def domain(self): return set()
    def interpret(self, term, assignment): return None
    def probability(self, world, event): return 1.0 if world in event else 0.0
    def preference(self, world, w1, w2): return False

model = EpistemicModel()
parser = UniLangParser()
engine = InferenceEngine.get_instance()

# Query: does the agent know p?
formula_p = parser.parse_string("K[agent] p")
result_p = engine.evaluate(formula_p, model, world=model.w0)  # evaluate at actual world w0
print(f"At world w0, agent knows p? {result_p}")

# Query: does the agent know q?
formula_q = parser.parse_string("K[agent] q")
result_q = engine.evaluate(formula_q, model, world=model.w0)
print(f"At world w0, agent knows q? {result_q}")
