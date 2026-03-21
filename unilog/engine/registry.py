
from typing import List
from ..ast import Formula
from .solvers import Solver
class SolverRegistry:
    def __init__(self): self._solvers: List[Solver] = []
    def register(self, solver: Solver): self._solvers.append(solver)
    def get_solver(self, formula: Formula)->Solver:
        for s in self._solvers:
            if s.supports(formula): return s
        raise ValueError(f'No solver for {type(formula).__name__}')
