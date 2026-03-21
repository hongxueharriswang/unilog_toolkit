from unilog.engine.model import Model, World

class WeatherModel(Model):
    def __init__(self):
        self.w1 = World('cloudy_rain')
        self.w2 = World('cloudy_dry')
        self.w3 = World('not_cloudy')
        self._worlds = {self.w1, self.w2, self.w3}
        self._probs = {self.w1: 0.32, self.w2: 0.08, self.w3: 0.60}
    def worlds(self): return self._worlds
    def valuation(self, w, atom, args):
        if atom == 'rain':
            return w == self.w1
        if atom == 'cloudy':
            return w in (self.w1, self.w2)
        return False
    def accessibility(self, world, modality, agent=None): return set()
    def domain(self): return set()
    def interpret(self, term, assignment): return None
    def probability(self, world, event):
        return sum(self._probs[w] for w in self._worlds if w in event)
    def preference(self, world, w1, w2): return False


def main():
    model = WeatherModel()
    rain_worlds = {w for w in model.worlds() if model.valuation(w, 'rain', ())}
    print(model.probability(None, rain_worlds))

if __name__ == '__main__':
    main()
