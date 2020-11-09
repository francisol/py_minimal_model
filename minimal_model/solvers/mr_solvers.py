#!/usr/bin/env python
from typing import Tuple

import pysat.solvers
import pysat.formula

import copy
from minimal_model.solvers.utils import *
from minimal_model.solvers.solvers import MMSolver, MRSolver
import minimal_model.utils


class MMSolverWithMR(MMSolver):
    """
     It extends MMSolver. This Solver use mr result of last step  in next step.
    """
    mr = True

    def compute_minimal_model(self) -> Tuple[bool, List[int]]:
        """
        This method is used to  a minimal model,it will return a `tuple`.
        The first value means whether a CNF formula given to the solver is satisfiability
        The second value is a minimal model only if the formula is satisfiability, otherwise the value is None\n
        :return:  (satisfiability,minimal model)
        """
        model = None
        start_cpu_time = minimal_model.utils.get_cpu_time()
        clauses = copy.deepcopy(self._formula.clauses)
        self._pysat_sovlver = pysat.solvers.Solver(self._pysat_name)
        self._pysat_sovlver.append_formula(self._formula)
        self._compute_model_count = 1
        while self._pysat_sovlver.solve():
            self._compute_model_count += 1
            model = self._pysat_sovlver.get_model()
            clauses = mr(clauses, model)
            self._pysat_sovlver.delete()
            self._pysat_sovlver = pysat.solvers.Solver(self._pysat_name)
            for clause in clauses:
                self._pysat_sovlver.add_clause(clause)
            positive_list = [-item for item in model if item > 0]
            self._pysat_sovlver.add_clause(positive_list)
        self._pysat_sovlver.delete()
        self._cpu_time = minimal_model.utils.get_cpu_time() - start_cpu_time
        return model is not None, model


class MRSolverWithMR(MRSolver):
    mr = True
    """
        It extends MRSolver. This Solver use mr result of last step  in next step. \n
    """

    def compute_minimal_model(self) -> Tuple[bool, List[int]]:
        """
        This method is used to  a minimal model,it will return a `tuple`.
        The first value means whether a CNF formula given to the solver is satisfiability
        The second value is a minimal model only if the formula is satisfiability, otherwise the value is None\n
        :return:  (satisfiability,minimal model)
        """
        start_cpu_time = minimal_model.utils.get_cpu_time()
        clauses = copy.deepcopy(self._formula.clauses)
        formula = copy.deepcopy(self._formula)
        model = None
        self._pysat_sovlver = pysat.solvers.Solver(self._pysat_name)
        self._pysat_sovlver.append_formula(self._formula)
        self._compute_model_count = 1
        self._check_model_count = 0
        while self._pysat_sovlver.solve():
            model = self._pysat_sovlver.get_model()
            clauses = mr(clauses, model)
            if self._check(copy.deepcopy(clauses), formula.nv, copy.deepcopy(model)):
                break
            self._pysat_sovlver.delete()
            self._pysat_sovlver = pysat.solvers.Solver(self._pysat_name)
            for clause in clauses:
                self._pysat_sovlver.add_clause(clause)
            positive_list = [-item for item in model if item > 0]
            self._pysat_sovlver.add_clause(positive_list)
            self._compute_model_count += 1
        self._pysat_sovlver.delete()
        self._cpu_time = minimal_model.utils.get_cpu_time() -start_cpu_time
        return model is not None, model
