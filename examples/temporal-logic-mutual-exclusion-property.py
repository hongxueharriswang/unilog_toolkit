"""
G (in_cs(A) -> not in_cs(B))

Model: A three‑state system:

State s0: no one in CS.

State s1: A in CS.

State s2: B in CS.
Transitions: s0 → s1, s0 → s2, s1 → s0, s2 → s0.

"""

from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine
from unilog.engine.model import Model, World
from unilog_toolkit.unilog.ast.nodes import Constant, Variable

class MutualExclusionModel(Model):
    def __init__(self):
        self.s0 = World('s0')
        self.s1 = World('s1')
        self.s2 = World('s2')
        self._worlds = {self.s0, self.s1, self.s2}
        self._transitions = {
            self.s0: [self.s1, self.s2],
            self.s1: [self.s0],
            self.s2: [self.s0],
        }

    def worlds(self): return self._worlds

    def valuation(self, world, atom, args):
        if atom == 'in_cs':
            if world == self.s1:
                return args == ('A',)
            if world == self.s2:
                return args == ('B',)
            return False
        return False

    def accessibility(self, world, modality, agent=None):
        # For temporal logic, we need a path relation; here we define a "next" relation.
        if modality == 'X':   # next
            return set(self._transitions.get(world, []))
        # For G and F, the engine would need to consider paths; our TemporalSolver is simplistic.
        # For demonstration, we'll just define accessibility for a single step.
        return set()

    def domain(self): return {'A', 'B'}
    def interpret(self, term, assignment):
        if isinstance(term, Variable):
            return assignment.get(term.name, None)
        if isinstance(term, Constant):
            return term.value
        return None
    def probability(self, world, event): return 1.0 if world in event else 0.0
    def preference(self, world, w1, w2): return False

model = MutualExclusionModel()
parser = UniLangParser()
engine = InferenceEngine.get_instance()

# Formula: G (in_cs(A) -> not in_cs(B))
formula = parser.parse_string("G (in_cs(A) -> not in_cs(B))")

# Evaluate at initial state s0
result = engine.evaluate(formula, model, world=model.s0)
print(f"Mutual exclusion holds from s0? {result}")
