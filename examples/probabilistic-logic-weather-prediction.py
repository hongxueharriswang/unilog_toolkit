"""
unilog

P_= 0.4 (cloudy)
P_= 0.8 (rain | cloudy)
P_>= ? (rain)   % we want to compute the probability of rain

"""

from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine
from unilog.engine.model import Model, World

class WeatherModel(Model):
    def __init__(self):
        self.w1 = World('cloudy_rain')      # cloudy & rain
        self.w2 = World('cloudy_dry')       # cloudy & no rain
        self.w3 = World('not_cloudy')       # not cloudy, no rain (assume no rain when not cloudy)
        self._worlds = {self.w1, self.w2, self.w3}
        self._probs = {
            self.w1: 0.4 * 0.8,      # 0.32
            self.w2: 0.4 * 0.2,      # 0.08
            self.w3: 0.6,             # 0.6
        }

    def worlds(self): return self._worlds

    def valuation(self, world, atom, args):
        if atom == 'cloudy':
            return world in (self.w1, self.w2)
        if atom == 'rain':
            return world == self.w1
        return False

    def accessibility(self, world, modality, agent=None): return set()
    def domain(self): return set()
    def interpret(self, term, assignment): return None

    def probability(self, world, event):
        # Probability measure: for a single world, probability is 1 if world in event else 0.
        # But we need to compute probability of an event across worlds.
        # The engine calls probability(world, event) when evaluating P_>= r (phi).
        # For a given world, it should return the probability of the event from that world's perspective.
        # In a static model, probability is the same for all worlds. We'll compute the measure of the event.
        if world == self.w1:
            # Return the total probability of event across all worlds? Actually the standard interpretation
            # of probability in modal logic: each world has its own probability distribution.
            # For simplicity, we'll treat the model as having a global probability measure.
            # We'll override the evaluation method differently.
            # Instead, we'll use a custom solver or compute directly.
            pass
        # For simplicity, we'll compute outside the engine.
        return 0.0

# Since the built‑in ProbabilisticSolver is not implemented in detail, we can compute manually.
model = WeatherModel()
total_rain_prob = sum(prob for w, prob in model._probs.items() if w in (model.w1,))
print(f"Probability of rain: {total_rain_prob}")

# To demonstrate the toolkit, we would need a proper probabilistic solver that can evaluate P_>= r (rain).
# We'll leave that as an exercise.
