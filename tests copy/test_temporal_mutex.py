from examples.temporal_mutex import MutualExclusionModel
from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine

def test_mutex_placeholder_true():
    parser = UniLangParser(); engine = InferenceEngine.get_instance(); m = MutualExclusionModel()
    phi = parser.parse_string("G (in_cs(A) -> not in_cs(B))")
    assert engine.evaluate(phi, m, world=m.s0) is True
