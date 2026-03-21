import unittest
from unilog.parser import UniLangParser

class TestParser(unittest.TestCase):
    def test_atom(self):
        parser = UniLangParser()
        f = parser.parse_string("p(x)")
        self.assertEqual(f.name, "p")
        self.assertEqual(len(f.args), 1)

    def test_and(self):
        parser = UniLangParser()
        f = parser.parse_string("p(x) and q(y)")
        self.assertIsInstance(f, AndFormula)

    def test_forall(self):
        parser = UniLangParser()
        f = parser.parse_string("forall x:S . p(x)")
        self.assertIsInstance(f, ForallFormula)
        self.assertEqual(f.var, "x")
        self.assertEqual(f.sort, "S")

if __name__ == '__main__':
    unittest.main()