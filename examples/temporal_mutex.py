from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine
from unilog.engine.model import Model, World
from unilog.ast import Variable, Constant

class MutualExclusionModel(Model):
    def __init__(self):
        self.s0 = World('s0')
        self.s1 = World('s1')
        self.s2 = World('s2')
        self._worlds = {self.s0, self.s1, self.s2}
        self._transitions = {self.s0: [self.s1, self.s2], self.s1: [self.s0], self.s2: [self.s0]}
    def worlds(self): return self._worlds
    def valuation(self, world, atom, args):
        if atom == 'in_cs':
            if world == self.s1:
                return args == ('A',)
            if world == self.s2:
                return args == ('B',)
        return False
    def accessibility(self, world, modality, agent=None):
        return set(self._transitions.get(world, [])) if modality == 'X' else set()
    def domain(self): return {'A', 'B'}
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
    model = MutualExclusionModel()
    result = engine.evaluate(parser.parse_string("G (in_cs(A) -> not in_cs(B))"), model, world=model.s0)
    print(result)

if __name__ == "__main__":
    main()
