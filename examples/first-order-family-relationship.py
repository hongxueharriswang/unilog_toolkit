"""
% Facts
parent(alice, bob)
parent(bob, charlie)
parent(alice, diana)

% Rules
forall x, y (parent(x,y) -> ancestor(x,y))
forall x, y, z (ancestor(x,y) and ancestor(y,z) -> ancestor(x,z))

% Query: Is Alice an ancestor of Charlie?
ancestor(alice, charlie)

"""

from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine
from unilog.engine.model import Model, World
from unilog.ast import *

class FamilyModel(Model):
    def __init__(self):
        self._world = World(0)
        self.facts = {
            ("parent", "alice", "bob"): True,
            ("parent", "bob", "charlie"): True,
            ("parent", "alice", "diana"): True,
        }
        self._domain = {"alice", "bob", "charlie", "diana"}

    def worlds(self): return {self._world}

    def valuation(self, world, atom, args):
        key = (atom,) + tuple(args)
        return self.facts.get(key, False)

    def accessibility(self, world, modality, agent=None): return set()
    def domain(self): return self._domain
    def interpret(self, term, assignment):
        if isinstance(term, Variable):
            return assignment.get(term.name, None)
        if isinstance(term, Constant):
            return term.value
        return None
    def probability(self, world, event): return 1.0 if world in event else 0.0
    def preference(self, world, w1, w2): return False

# Parse and evaluate
parser = UniLangParser()
engine = InferenceEngine.get_instance()

# Define the query (ancestor(alice, charlie))
query = parser.parse_string("ancestor(alice, charlie)")

# We need to define ancestor using the rules; the inference engine does not automatically apply rules.
# Instead, we can evaluate a conjunction of facts and rules that imply the query.
# For simplicity, we'll evaluate the query directly if we had pre‑computed ancestor facts.
# In a real system, we would use a rule engine; here we just check if the fact is directly present.

model = FamilyModel()
result = engine.evaluate(query, model)
print(f"Is Alice an ancestor of Charlie? {result}")  # False (since not directly asserted)

# To actually deduce ancestor, we would need a forward‑chaining engine or to evaluate the rules separately.
# We can manually compute closure or use the engine to check if the rules are satisfied given the facts.
# Here we just show the basic usage.

"""
Interpretation: The direct fact ancestor(alice, charlie) is not present; the toolkit evaluates atomic formulas directly from the model's valuation. A full rule‑based system would require a forward‑chaining or resolution engine, which is beyond the scope of the current toolkit (which focuses on evaluating formulas against a given model). This example illustrates the need to pre‑compute or include derived facts in the model.
"""