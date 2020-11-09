#!/usr/bin/env python
from typing import Tuple

import pysat.solvers
import pysat.formula
from pysat.formula import CNF
from minimal_model.graph import Graph, StronglyConnectedGraph
import copy
from minimal_model.solvers.utils import *
import minimal_model.utils


class _BaseSolver(object):
    """
    define some basic function
    """

    def __init__(self, pysat_name="m22", bootstrap_with=None):
        """
        :param pysat_name :The name of  SAT's solver
        """
        self._pysat_sovlver = None
        self._compute_model_count = 0
        self._pysat_name = pysat_name
        self._formula = CNF()
        self._cpu_time = 0.0
        if bootstrap_with:
            self._formula.from_clauses(bootstrap_with)

    def print_status(self):
        used_mem = minimal_model.utils.get_used_memory()
        print("Memory used           : %.2f MB" % used_mem)
        print("CPU time              : %g s" % self.cpu_time)
        print("ComputeModelCount     : %d " % self.compute_model_count)

    @property
    def compute_model_count(self) -> int:
        return self._compute_model_count

    @property
    def cpu_time(self) -> float:
        """
        get the cpu time of solving minimal model
        """
        return self._cpu_time

    @property
    def formula(self) -> CNF:
        """
        get the original CNF formula
        """
        return self._formula

    def add_clause(self, clause):
        """
        add clause to formula
        """
        self._formula.append(clause)

    def append_formula(self, formula):
        """
        append formula to formula
        """
        for clause in formula.clauses:
            self._formula.append(clause)

    def compute_minimal_model(self) -> Tuple[bool, list]:
        """
        This method is used to  a minimal model,it will return a `tuple`.
        The first value means whether a CNF formula given to the solver is satisfiability
        The second value is a minimal model only if the formula is satisfiability, otherwise the value is None\n
        :return:  (satisfiability,minimal model)
        """
        pass


class MMSolver(_BaseSolver):
    names = ["MM"]
    """
    This  solver compute minimal model without check \n When pysat get a model ,next, solver will get
    a new model that is subset of last model and check it. until find a minimal model.\n The solver also proxy
    pysat's solver function, ie you can call  such as `append_formula`
    """

    def __getattr__(self, name):
        return getattr(self._pysat_sovlver, name)

    def __init__(self, pysat_name='m22', bootstrap_with=None):
        """
            This  solver compute minimal model without check \n When pysat get a model ,next, solver will get
            a new model that is subset of last model and check it. until find a minimal model.\n The solver also proxy
            pysat's solver function, ie you can call  such as `append_formula`
        :param pysat_name :The name of  SAT's solver, t will be used to instantiate pysat.solvers.Solver as param named pysat_name
        :param bootstrap_with: it will be used to instantiate pysat.solvers.Solver as param named bootstrap_with
        """
        super().__init__(pysat_name, bootstrap_with)

    def compute_minimal_model(self) -> Tuple[bool, List[int]]:
        """
        This method is used to  a minimal model,it will return a `tuple`.
        The first value means whether a CNF formula given to the solver is satisfiability
        The second value is a minimal model only if the formula is satisfiability, otherwise the value is None\n
        :return:  (satisfiability,minimal model)
        """
        start_cpu_time = minimal_model.utils.get_cpu_time()
        model = None
        self._pysat_sovlver = pysat.solvers.Solver(self._pysat_name)
        self._pysat_sovlver.append_formula(self._formula)
        self._compute_model_count = 1
        while self._pysat_sovlver.solve():
            self._compute_model_count += 1
            model = self._pysat_sovlver.get_model()
            positive_list = []
            for item in model:
                if item > 0:
                    positive_list.append(-item)
                else:
                    self._pysat_sovlver.add_clause([item])
            self._pysat_sovlver.add_clause(positive_list)
        self._cpu_time = minimal_model.utils.get_cpu_time() - start_cpu_time
        self._pysat_sovlver.delete()
        return model is not None, model


class MRSolver(_BaseSolver):
    """
        It compute minimal model with check. \n
        When pysat get a model ,this solver will check whether it's a minimal model. if it is, solver will return model ,
        otherwise solver will get a new model that is subset of last model and check it. until find a minimal model.
    """
    names = ["MR"]

    def __init__(self, pysat_name='m22', pysat_check_name='', bootstrap_with=None):
        """
        It compute minimal model with check. \n When pysat get a model ,this solver will check whether it's a minimal
        model. if it is, solver will return model , otherwise solver will get a new model that is subset of last
        model and check it. until find a minimal model.
        :param pysat_name  The name of  SAT's solver, t will be used
        to instantiate pysat.solvers.Solver for computing  as param named pysat_name
        :param bootstrap_with: it will
        be used to instantiate pysat.solvers.Solver for computing as param named bootstrap_with
        :param pysat_check_name The name of  SAT's solver for checking, t will be used to instantiate pysat.solvers.Solver
        for checking as param named pysat_name
        """
        super().__init__(pysat_name, bootstrap_with)
        self._pysat_check_name = pysat_check_name if pysat_check_name != '' else pysat_name
        self._check_model_count = 0

    @property
    def check_model_count(self):
        return self._check_model_count

    def _compute(self, ts, s) -> bool:
        """
        compute whether  s is the minimal model of ts
        :param ts: clauses
        :param s: atom set
        :return: True if s is the minimal model of ts
        """
        if len(ts) == 0:
            return len(s) == 0
        if len(s) == 1:
            for clause in ts.values():
                body = [x for x in clause if x < 0]
                if body:
                    return False
            return True
        check_solver = pysat.solvers.Solver(self._pysat_check_name)

        for clause in ts.values():
            if clause:
                check_solver.add_clause(clause)
        check_solver.add_clause([-x for x in s])
        result = check_solver.solve()
        check_solver.delete()
        return not result

    def print_status(self):
        super().print_status()
        print("CheckModelCount       : {} ".format(self.check_model_count))

    def _check(self, clauses: list, formula_nv: int, model) -> bool:
        """
        This method is used to check whether the model given in parameters is a minimal model of clauses given in
        parameters
        """
        self._check_model_count += 1
        mr_clauses = mr(clauses, model)
        graph = create_graph(mr_clauses, formula_nv)
        scc = StronglyConnectedGraph(graph)
        node = scc.get_one_empty_indegree()
        while node:
            if node is None:
                break
            if node > formula_nv:
                scc.remove(node)
                node = scc.get_one_empty_indegree()
                continue
            s = compute_s(scc.scc_weights[node], formula_nv)
            ts = compute_ts(mr_clauses, s, formula_nv)
            if self._compute(ts, s):
                model = [-x if x in s else x for x in model]
                mr_clauses = reduce(mr_clauses, s)
                scc.remove(node)
                node = scc.get_one_empty_indegree()
            else:
                break
        header = [x for x in model if x > 0]
        return len(header) == 0

    def compute_minimal_model(self) -> Tuple[bool, List[int]]:
        """
        This method is used to  a minimal model,it will return a `tuple`.
        The first value means whether a CNF formula given to the solver is satisfiability
        The second value is a minimal model only if the formula is satisfiability, otherwise the value is None\n
        :return:  (satisfiability,minimal model)
        """
        start_cpu_time = minimal_model.utils.get_cpu_time()
        model = None
        formula = copy.deepcopy(self._formula)
        self._compute_model_count = 1
        self._check_model_count = 0
        self._pysat_sovlver = pysat.solvers.Solver(self._pysat_name)
        self._pysat_sovlver.append_formula(self._formula)
        while self._pysat_sovlver.solve():
            model = self._pysat_sovlver.get_model()
            if self._check(formula.clauses, formula.nv, copy.deepcopy(model)):
                break
            positive_list = []
            for item in model:
                if item > 0:
                    positive_list.append(-item)
                else:
                    self._pysat_sovlver.add_clause([item])
            self._pysat_sovlver.add_clause(positive_list)
            self._compute_model_count += 1
        self._cpu_time = minimal_model.utils.get_cpu_time() - start_cpu_time
        self._pysat_sovlver.delete()
        return model is not None, model
