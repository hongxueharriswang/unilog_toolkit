
from typing import Optional, Dict, Any, Union
from ..ast import Formula
from .model import Model, World
from .registry import SolverRegistry
from .solvers import ClassicalSolver, ModalSolver, TemporalSolver, FuzzySolver
from .solvers_external import DefaultLogicSolver, SMTSolver, ProbabilisticSolver
class InferenceEngine:
    _instance=None
    def __init__(self):
        self.registry = SolverRegistry(); self._register_default_solvers()
    @classmethod
    def get_instance(cls):
        if cls._instance is None: cls._instance = cls()
        return cls._instance
    def _register_default_solvers(self):
        self.registry.register(ClassicalSolver())
        self.registry.register(ModalSolver())
        self.registry.register(TemporalSolver())
        self.registry.register(FuzzySolver())
        # External adapters
        self.registry.register(DefaultLogicSolver())
        self.registry.register(SMTSolver())
        self.registry.register(ProbabilisticSolver())
    def register_solver(self, solver): self.registry.register(solver)
    def evaluate(self, formula: Formula, model: Model, world: Optional[World]=None, assignment: Optional[Dict[str,Any]]=None)->Union[bool,float]:
        if world is None:
            ws=list(model.worlds())
            if not ws: raise ValueError('Model has no worlds')
            world=ws[0]
        if assignment is None: assignment={}
        solver = self.registry.get_solver(formula)
        return solver.evaluate(formula, model, world, assignment)
