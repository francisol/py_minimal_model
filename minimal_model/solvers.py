#!/usr/bin/env python
import pysat.solvers
import pysat.formula
from pysat.formula import CNF
from .graph import Graph, StronglyConnectedGraph
import copy
from .utils import mr

SoloverMap = {
    "MM": 'MMSolver',
    'MR': 'MRSolver'
    # 'MMSolver': 'MMSolver',
}


class Solver:
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
            clz_name = SoloverMap[name]
            clz = glob[clz_name]
            self._real_solver = clz(**kwargs)
        else:
            if name == self.__class__.__name__:
                raise RuntimeError('cannot create solver named [{}]'.format(name))
            if name in glob:
                clz = glob[name]
                self._real_solver = clz(**kwargs)
            else:
                raise RuntimeError('no solver named [{}]'.format(name))
        print('compute minimal model use ', name)

    def __getattr__(self, name):
        """
        Proxy specific solver
        """
        return getattr(self._real_solver, name)




class MMSolver(object):
    """
        This is specific solver, it compute minimal model without check \n
        When pysat get a model ,next, solver will get a new model that is subset of last model and check it. until find a minimal model.\n
        The solver also proxy  pysat's solver functuon, ie you can call  such as `append_formula`
    """

    def __getattr__(self, name):
        return getattr(self._pysat_sovlver, name)

    def __init__(self, pysat_name='m22', bootstrap_with=None, **kwargs):
        self._pysat_sovlver = None
        self.compute_model_count = 0
        self._pysat_name = pysat_name
        self._kwargs = kwargs
        self._formula = CNF()
        if bootstrap_with:
            self._formula.from_clauses(bootstrap_with)

    def add_clause(self, clause, **kwargs):
        self._formula.append(clause)

    def append_formula(self, formula, **kwargs):
        for clause in formula.clauses:
            self._formula.append(clause)

    def compute_minimal_model(self):
        model = None
        '''
        This method is used to  a minimal model,it will return a `tuple`.
        The first value means whether a CNF formula given to the solver is satisfiability
        The second value is a minimal model only if the formula is satisfiability, otherwise the value is None\n
        :returnType (Boolean,list)
        '''
        # if self.compute_model_count > 0:
        #     raise RuntimeError("this function can not be called repeatly")
        if self._pysat_sovlver:
            self._pysat_sovlver.delete()
        self._pysat_sovlver = pysat.solvers.Solver(self._pysat_name, **self._kwargs)
        self._pysat_sovlver.append_formula(self._formula)
        self.compute_model_count = 1
        while self._pysat_sovlver.solve():
            self.compute_model_count += 1
            model = self._pysat_sovlver.get_model()
            positive_list = []
            for item in model:
                if item > 0:
                    positive_list.append(-item)
                else:
                    self._pysat_sovlver.add_clause([item])
            self._pysat_sovlver.add_clause(positive_list)
        return model is not None, model


class MRSolver(object):
    """
        This is specific solver, it compute minimal model with check. \n
        When pysat get a model ,this solver will check whether it's a minimal model. if it is, solver will return model ,
        otherwise solver will get a new model that is subset of last model and check it. until find a minimal model. \n
        The solver also proxy  pysat's solver functuon, ie you can call  such as `append_formula`
    """

    def __getattr__(self, name):
        return getattr(self._pysat_sovlver, name)

    def add_clause(self, clause, **kwargs):
        self._formula.append(clause)
        return self._pysat_sovlver.add_clause(clause, **kwargs)

    def append_formula(self, formula, **kwargs):
        for clause in formula.clauses:
            self._formula.append(clause)

    def __init__(self, pysat_name='m22', pysat_check_name='', bootstrap_with=None, **kwargs):
        self._pysat_sovlver = pysat.solvers.Solver(pysat_name, **kwargs)
        self._pysat_check_name = pysat_check_name if pysat_check_name != '' else pysat_name
        self._formula = CNF()
        self.compute_model_count = 0
        self.check_model_count = 0
        if bootstrap_with:
            self._formula.from_clauses(bootstrap_with)

    def _create_graph(self, clauses, formula_nv):
        key = formula_nv + 1
        graph = Graph()
        for clause in clauses:
            for atom in clause:
                if atom > 0:
                    graph.add_point(key, atom)
                else:
                    graph.add_point(-atom, key)
            key += 1
        return graph


    def _compute_ts(self, clauses, weights,formula_nv):
        ts = {}
        key = formula_nv
        for clause in clauses:
            c = {abs(x) for x in clause}
            if c.issubset(weights) and clause:
                ts[key] = clause
            key += 1
        return ts

    def _compute_s(self, component, limit):
        return {x for x in component if x <= limit}

    def _compute(self, ts, s):
        if len(ts) == 0:
            return len(s) != 0
        if len(s) == 1:
            for clause in ts.values():
                body = [x for x in clause if x < 0]
                if body:
                    return True
            return False
        check_solver = pysat.solvers.Solver(self._pysat_check_name)

        for clause in ts.values():
            if clause:
                check_solver.add_clause(clause)
        check_solver.add_clause([-x for x in s])
        result = check_solver.solve()
        check_solver.delete()
        return result

    def _reduce(self, clauses, s):
        for clause in clauses:
            header = {x for x in clause if x > 0}
            if header.intersection(s):
                clause.clear()
                continue
            c = [x for x in clause if abs(x) not in s]
            clause.clear()
            clause.extend(c)

    def _check(self, clauses:list, formula_nv:int,model):
        """
        This method is used to check whether the model given in parameters is a minimal model of clauses given in parameters
        The algorithm refer to
        """
        self.check_model_count += 1
        mr_clauses = mr(clauses, model)
        graph = self._create_graph(mr_clauses,formula_nv)
        scc = StronglyConnectedGraph(graph)
        node = scc.get_one_empty_indegree()
        while node:
            if node is None:
                break
            if node > formula_nv:
                scc.remove(node)
                node = scc.get_one_empty_indegree()
                continue
            s = self._compute_s(scc.scc_weights[node], formula_nv)
            ts = self._compute_ts(mr_clauses, s,formula_nv)
            if not self._compute(ts, s):
                model = [-x if x in s else x for x in model]
                self._reduce(mr_clauses, s)
                mr_clauses = [x for x in mr_clauses if x]
                scc.remove(node)
                node = scc.get_one_empty_indegree()
            else:
                break
        header = [x for x in model if x > 0]
        return len(header) == 0

    def compute_minimal_model(self):
        """
        This method is used to  a minimal model,it will return a `tuple`.
        The first value means whether a CNF formula given to the solver is satisfiability
        The second value is a minimal model only if the formula is satisfiability, otherwise the value is None\n
        :returnType (Boolean,list)
        """
        model = None
        formula = copy.deepcopy(self._formula)
        if self._pysat_sovlver:
            self._pysat_sovlver.delete()

        self.compute_model_count = 1
        while self._pysat_sovlver.solve():
            model = self._pysat_sovlver.get_model()
            if self._check(formula.clauses,formula.nv ,copy.deepcopy(model)):
                break
            positive_list = []
            for item in model:
                if item > 0:
                    positive_list.append(-item)
                else:
                    self._pysat_sovlver.add_clause([item])
            self._pysat_sovlver.add_clause(positive_list)
            self.compute_model_count += 1
        return model is not None, model
