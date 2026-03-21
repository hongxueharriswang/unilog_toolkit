from examples.fuzzy_temp import FuzzyModel
from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine

def test_fuzzy_threshold_true():
    parser = UniLangParser(); engine = InferenceEngine.get_instance(); m = FuzzyModel()
    assert engine.evaluate(parser.parse_string("T_>= 0.5 (high(30))"), m) is True
