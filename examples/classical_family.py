from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine
from unilog.engine.model import Model, World
from unilog.ast import Variable, Constant

class FamilyModel(Model):
    def __init__(self):
        self.w = World(0)
        self.facts = {
            ("parent", "alice", "bob"): True,
            ("parent", "bob", "charlie"): True,
            ("parent", "alice", "diana"): True,
            # derived/transitive closure for this example only
            ("ancestor", "alice", "bob"): True,
            ("ancestor", "bob", "charlie"): True,
            ("ancestor", "alice", "charlie"): True,
        }
        self._domain = {"alice", "bob", "charlie", "diana"}
    def worlds(self): return {self.w}
    def valuation(self, world, atom, args):
        return self.facts.get((atom,) + tuple(args), False)
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


def main():
    parser = UniLangParser()
    engine = InferenceEngine.get_instance()
    model = FamilyModel()
    query = parser.parse_string("ancestor(alice, charlie)")
    result = engine.evaluate(query, model)
    print(result)

if __name__ == "__main__":
    main()
