from examples.prob_weather import WeatherModel

def test_prob_rain():
    m = WeatherModel()
    rain_event = {w for w in m.worlds() if m.valuation(w, 'rain', ())}
    assert abs(m.probability(None, rain_event) - 0.32) < 1e-9
