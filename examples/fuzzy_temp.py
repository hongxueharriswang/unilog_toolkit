from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine
from unilog.engine.model import Model, World
from unilog.ast import Function, Constant

class FuzzyModel(Model):
    def __init__(self):
        self._world = World(0)
    def worlds(self): return {self._world}
    def valuation(self, world, atom, args): return False
    def accessibility(self, world, modality, agent=None): return set()
    def domain(self): return set()
    def interpret(self, term, assignment):
        if isinstance(term, Function) and term.name == 'high':
            arg = term.args[0]
            if isinstance(arg, Constant):
                x = arg.value
                return max(0.0, min(1.0, (x - 25) / 10))
        return None
    def probability(self, world, event): return 1.0 if world in event else 0.0
    def preference(self, world, w1, w2): return False


def main():
    parser = UniLangParser()
    engine = InferenceEngine.get_instance()
    model = FuzzyModel()
    formula = parser.parse_string("T_>= 0.5 (high(30))")
    print(engine.evaluate(formula, model))

if __name__ == '__main__':
    main()
