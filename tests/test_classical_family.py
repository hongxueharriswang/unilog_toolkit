from examples.classical_family import FamilyModel
from unilog.parser import UniLangParser
from unilog.engine import InferenceEngine

def test_ancestor_true():
    parser = UniLangParser()
    engine = InferenceEngine.get_instance()
    model = FamilyModel()
    q = parser.parse_string("ancestor(alice, charlie)")
    assert engine.evaluate(q, model) is True
