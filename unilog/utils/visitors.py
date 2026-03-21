from ..ast import *

class PrettyPrinter:
    def visit(self, formula):
        return formula.accept(self)

    def visit_atom(self, formula):
        args = ', '.join(str(a) for a in formula.args)
        return f"{formula.name}({args})"

    def visit_and(self, formula):
        return f"({self.visit(formula.left)} and {self.visit(formula.right)})"

    def visit_or(self, formula):
        return f"({self.visit(formula.left)} or {self.visit(formula.right)})"

    def visit_implies(self, formula):
        return f"({self.visit(formula.left)} -> {self.visit(formula.right)})"

    def visit_iff(self, formula):
        return f"({self.visit(formula.left)} <-> {self.visit(formula.right)})"

    def visit_not(self, formula):
        return f"not {self.visit(formula.sub)}"

    def visit_forall(self, formula):
        return f"forall {formula.var}:{formula.sort}. {self.visit(formula.body)}"

    def visit_exists(self, formula):
        return f"exists {formula.var}:{formula.sort}. {self.visit(formula.body)}"

    # ... similar for other node types

class SubstitutionVisitor:
    def __init__(self, var: str, term: Term):
        self.var = var
        self.term = term

    def visit(self, formula):
        return formula.accept(self)

    # ... implement substitution for each node