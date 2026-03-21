def test_imports():
    import unilog
    from unilog.parser import UniLangParser
    from unilog.engine import InferenceEngine
    from unilog.engine.model import Model, World
    assert UniLangParser and InferenceEngine and Model and World
