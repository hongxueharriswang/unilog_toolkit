from examples.modal_epistemic import EpistemicModel
from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine

def test_knowledge_false_at_w0():
    parser = UniLangParser(); engine = InferenceEngine.get_instance(); m = EpistemicModel()
    assert engine.evaluate(parser.parse_string("K[agent] p"), m, world=m.w0) is False
    assert engine.evaluate(parser.parse_string("K[agent] q"), m, world=m.w0) is False
