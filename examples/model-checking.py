from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine
from unilog.engine.model import Model, World

# Define a simple Kripke structure with two worlds
class KripkeModel(Model):
    def __init__(self):
        self.w0 = World(0)
        self.w1 = World(1)
    def worlds(self): return {self.w0, self.w1}
    def valuation(self, world, atom, args):
        if world == self.w0:
            return atom == 'p' and args == ()
        else:
            return atom == 'q' and args == ()
    def accessibility(self, world, modality, agent):
        # one transition: w0 -> w1
        if world == self.w0:
            return {self.w1}
        else:
            return set()
    # ... other methods (domain, interpret, probability, preference) ...

model = KripkeModel()
parser = UniLangParser()
formula = parser.parse_string("p -> AX q")  # if p then on all next paths q
engine = InferenceEngine.get_instance()
result = engine.evaluate(formula, model)
print(result)  # True