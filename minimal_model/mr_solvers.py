#!/usr/bin/env python
import pysat.solvers
import pysat.formula
from pysat.formula import CNF
from .graph import Graph, StronglyConnectedGraph
import copy
from .utils import mr
from .solvers import MMSolver, MRSolver

SoloverMap = {
    "MM": 'MMSolverWithMR',
    'MR': 'MRSolverWithMR'
    # 'MMSolver': 'MMSolver',
}


class Solver(object):
    """
        This class can  proxy a specific solver by solver's name or short name. \n
        The constructor need a   solver's name or short name ,other parameter will be given specific solver's constructor
    """

    def __init__(self, name='MM', **kwargs):
        """
        constructor
        """
        glob = globals()
        if name in SoloverMap:
            clas_name = SoloverMap[name]
            clas = glob[clas_name]
            self.__real_solver = clas(**kwargs)
        else:
            if name == self.__class__.__name__:
                raise RuntimeError('cannot create solver named [{}]'.format(name))
            if name in glob:
                clas = glob[name]
                self.__real_solver = clas(**kwargs)
            else:
                raise RuntimeError('no solver named [{}]'.format(name))
        print('compute minimal model use ', name, ' with mr ')

    def __getattr__(self, name):
        """
        Proxy specific solver
        """
        return getattr(self.__real_solver, name)


class MMSolverWithMR(MMSolver):
    """
        This is specific solver, it compute minimal model without check \n
        When pysat get a model ,next, solver will get a new model that is subset of last model and check it. until find a minimal model.\n
        The solver also proxy  pysat's solver functuon, ie you can call  such as `append_formula`
    """

    def compute_minimal_model(self):
        model = None
        """
        This method is used to  a minimal model,it will return a `tuple`.
        The first value means whether a CNF formula given to the solver is satisfiability
        The second value is a minimal model only if the formula is satisfiability, otherwise the value is None\n
        :returnType (Boolean,Array)
        """
        clauses = copy.deepcopy(self._formula.clauses)
        if self._pysat_sovlver:
            self._pysat_sovlver.delete()
        self._pysat_sovlver = pysat.solvers.Solver(self._pysat_name, **self._kwargs)
        self._pysat_sovlver.append_formula(self._formula)
        self.compute_model_count = 1
        while self._pysat_sovlver.solve():
            self.compute_model_count += 1
            model = self._pysat_sovlver.get_model()
            clauses = mr(clauses, model)
            self._pysat_sovlver.delete()
            self._pysat_sovlver = pysat.solvers.Solver(self._pysat_name, **self._kwargs)
            for clause in clauses:
                self._pysat_sovlver.add_clause(clause)
            positive_list = [-item for item in model if item > 0]
            self._pysat_sovlver.add_clause(positive_list)
        self._pysat_sovlver.delete()
        return model is not None, model


class MRSolverWithMR(MRSolver):
    """
        This is specific solver, it compute minimal model with check. \n
        When pysat get a model ,this solver will check whether it's a minimal model. if it is, solver will return model ,
        otherwise solver will get a new model that is subset of last model and check it. until find a minimal model. \n
        The solver also proxy  pysat's solver functuon, ie you can call  such as `append_formula`
    """

    def compute_minimal_model(self):
        """
        This method is used to  a minimal model,it will return a `tuple`.
        The first value means whether a CNF formula given to the solver is satisfiability
        The second value is a minimal model only if the formula is satisfiability, otherwise the value is None\n
        :returnType (Boolean,list)
        """
        clauses = copy.deepcopy(self._formula.clauses)
        formula = copy.deepcopy(self._formula)
        model = None
        if self._pysat_sovlver:
            self._pysat_sovlver.delete()
        self._pysat_sovlver = pysat.solvers.Solver(self._pysat_name, **self.kwargs)
        self.compute_model_count = 1
        while self._pysat_sovlver.solve():
            model = self._pysat_sovlver.get_model()
            clauses = mr(self._clauses, model)
            if self._check(copy.deepcopy(clauses), formula.nv, copy.deepcopy(model)):
                break
            self._pysat_sovlver.delete()
            self._pysat_sovlver = pysat.solvers.Solver(self._pysat_name, **self.kwargs)
            for clause in clauses:
                self._pysat_sovlver.add_clause(clause)
            positive_list = [-item for item in model if item > 0]
            self._pysat_sovlver.add_clause(positive_list)
            self.compute_model_count += 1
        self._pysat_sovlver.delete()
        return model is not None, model
