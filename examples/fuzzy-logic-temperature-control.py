"""
unilog
high(30)  % fuzzy predicate application
T_>= 0.5 (cooling_on)   % we want to know if cooling_on is at least 0.5

"""

from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine
from unilog.engine.model import Model, World
from unilog_toolkit.unilog.ast.nodes import Constant, Constant, Function

class FuzzyModel(Model):
    def __init__(self, temp):
        self.temp = temp
        self._world = World(0)

    def worlds(self): return {self._world}

    def valuation(self, world, atom, args):
        # For fuzzy predicates, we return a float instead of bool.
        # But the Model interface expects bool. We'll handle via interpret.
        # Instead, we'll treat high as a function that returns a float, and use GradedTruth.
        return False   # not used

    def accessibility(self, world, modality, agent=None): return set()
    def domain(self): return set()

    def interpret(self, term, assignment):
        # term is something like Function('high', [Constant(30)])
        if isinstance(term, Function) and term.name == 'high':
            arg = term.args[0]
            if isinstance(arg, Constant):
                x = arg.value
                # membership function
                return max(0.0, min(1.0, (x - 25) / 10))
        return None

    def probability(self, world, event): return 1.0 if world in event else 0.0
    def preference(self, world, w1, w2): return False

model = FuzzyModel(temp=30)
parser = UniLangParser()
engine = InferenceEngine.get_instance()

# Formula: cooling_on should be at least 0.5 based on rule: cooling_on = high(temp)
# We can't directly compute cooling_on; we need to evaluate high(temp) and then decide.
# We'll evaluate high(temp) as a term.
# In UniLang, we might write: T_>= 0.5 (high(30))
formula = parser.parse_string("T_>= 0.5 (high(30))")
result = engine.evaluate(formula, model)
print(f"Is cooling_on ≥ 0.5? {result}")

# Compute the actual truth value:
truth = model.interpret(Function('high', [Constant(30)]), {})
print(f"Actual truth value of high(30): {truth}")