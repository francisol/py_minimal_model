#!/usr/bin/env python
import pysat.solvers
import pysat.formula
from pysat.formula import CNF
from .graph import Graph,StronglyConnectedGraph
import copy

SoloverMap = {
    "MM": 'MMSolver',
    'MR':'MRSolver'
    # 'MMSolver': 'MMSolver',
}
class Solver():
    '''
        This class can  proxy a specific solver by solver's name or short name. \n
        The constructor need a   solver's name or short name ,other parameter will be given specific solver's constructor
    '''

    def __init__(self, name='MM', **kwargs):
        '''
        constructor
        '''
        glob = globals()
        if name in SoloverMap:
            clas_name = SoloverMap[name]
            clas = glob[clas_name]
            self.__real_solver = clas(**kwargs)
        else:
            if name == self.__class__.__name__:
                raise RuntimeError('cannot create solver named [{}]'.format(name))
            if name in glob:
                clas=glob[name]
                self.__real_solver = clas(**kwargs)
            else:
                raise RuntimeError('no solver named [{}]'.format(name))


    def __getattr__(self, name):
        '''
        Proxy specific solver
        '''
        return getattr(self.__real_solver,name)


class MMSolver(object):
    '''
        This is specific solver, it compute minimal model without check \n
        When pysat get a model ,next, solver will get a new model that is subset of last model and check it. until find a minimal model.\n
        The solver also proxy  pysat's solver functuon, ie you can call  such as `append_formula`
    '''
    def __getattr__(self, name):
        return getattr(self.__pysat_sovlver,name)
        
    def __init__(self,pysat_name='m22',bootstrap_with=None,**kwargs):
        self.__pysat_sovlver = pysat.solvers.Solver(pysat_name, **kwargs)
        self.compute_model_count = 0
    def compute_minimal_model(self):
        '''
        This method is used to  a minimal model,it will return a `tuple`.
        The first value means whether a CNF formula given to the solver is satisfiability
        The second value is a minimal model only if the formula is satisfiability, otherwise the value is None\n
        :returnType (Boolean,list)
        '''
        if self.compute_model_count >0:
            raise RuntimeError("this function can not be called repeatly")
        self.compute_model_count=1
        while self.__pysat_sovlver.solve():
            self.compute_model_count+=1
            model = self.__pysat_sovlver.get_model()
            positive_list=[]
            for item in model:
                if item >0:
                    positive_list.append(-item)
                else:
                    self.__pysat_sovlver.add_clause([item])
            self.__pysat_sovlver.add_clause(positive_list)
        return (model is not None ,model)



class MRSolver(object):
    '''
        This is specific solver, it compute minimal model with check. \n
        When pysat get a model ,this solver will check whether it's a minimal model. if it is, solver will return model ,
        otherwise solver will get a new model that is subset of last model and check it. until find a minimal model. \n
        The solver also proxy  pysat's solver functuon, ie you can call  such as `append_formula`
    '''
    def __getattr__(self, name):
        return getattr(self.__pysat_sovlver,name)
    
    def add_clause(self, clause,**kwargs):
        self.__formula.append(clause)
        return self.__pysat_sovlver.add_clause(clause, **kwargs)
    
    def append_formula(self, formula, **kwargs):
        for clause in formula.clauses:
            self.__formula.append(clause)
        self.__pysat_sovlver.append_formula(formula, **kwargs)

    def __init__(self, pysat_name='m22', pysat_mr_name='',bootstrap_with=None, **kwargs):
        self.__pysat_sovlver = pysat.solvers.Solver(pysat_name, **kwargs)
        self.__pysat_mr_name = pysat_mr_name if pysat_mr_name != '' else pysat_name
        self.__formula = CNF()
        self.compute_model_count=0
        self.check_model_count=0
        if bootstrap_with:
            for clause in bootstrap_with:
                self.add_clause(clause)

    def __create_graph(self,clauses):
        key = self.__formula.nv+1
        graph = Graph()
        for clause in clauses:
            for atom in clause:
                if atom > 0:
                    graph.add_point(key, atom)
                else:
                    graph.add_point(-atom, key)
            key += 1
        return graph

    def __mr(self, clauses,model):
        # positive_model = set([x for x in model if x > 0])
        negativ_model = set([x for x in model if x < 0])
        result =[]
        for clause in clauses:
            # header = [x for x in clause if x > 0]
            body = [x for x in clause if x < 0]
            if set(body).intersection(negativ_model):
                continue
            c = [x for x in clause if -x not in negativ_model]
            result.append(c)
        return result

    def __compute_ts(self, clauses,weights):
        ts = {}
        key = self.__formula.nv
        for clause in clauses:
            c = {abs(x) for x in clause}
            if c.issubset(weights):
                ts[key] = clause
            key += 1
        return ts
    
    def __compute_s(self, graph, limit):
        s = set()
        for node in graph.empty_indegree():
            s.update([x for x in graph.scc_weights[node] if x <= limit])
        return s

    def __compute(self, ts, s):
        if len(ts) == 0:
            return len(s) == 0
        if len(s) == 1:
            for clause in ts.values():
                body = [x for x in clause if x < 0]
                if body:
                    return False
        solver = pysat.solvers.Solver(self.__pysat_mr_name)

        for clause in ts.values():
            solver.add_clause(clause)
        solver.add_clause([-x for x in s])
        return solver.solve()
    
    def __reduce(self, clauses, s):
        for clause in clauses:
            header = {x for x in clause if x > 0}
            if header.intersection(s):
                clause.clear()
                continue
            c = [x for x in clause if abs(x) not in s]
            clause.clear()
            clause.extend(c)

    def __check(self, clauses, model):
        '''
        This method is used to check whether the model be given in parameters is a minimal model of clauses be given in parameters
        The algorithm refer to
        '''
        self.check_model_count += 1
        mr_clauses = self.__mr(clauses, model)
        graph = self.__create_graph(mr_clauses)
        scc = StronglyConnectedGraph(graph)
        node = scc.get_one_empty_indegree()
        while node :
            if node is None:
                break
            if node > self.__formula.nv:
                scc.remove(node)
                node = scc.get_one_empty_indegree()
                continue
            ts = self.__compute_ts(mr_clauses, scc.scc_weights[node])
            s = self.__compute_s(scc, self.__formula.nv)
            if not self.__compute(ts,s):
                model = [-x if x in s else x for x in model]
                self.__reduce(mr_clauses, s)
                scc.remove(node)
                node = scc.get_one_empty_indegree()
            else:
                break
        header = [x for x in model if x > 0]
        return len(header)==0
            

    def compute_minimal_model(self):
        '''
        This method is used to  a minimal model,it will return a `tuple`.
        The first value means whether a CNF formula given to the solver is satisfiability
        The second value is a minimal model only if the formula is satisfiability, otherwise the value is None\n
        :returnType (Boolean,list)
        '''
        if self.compute_model_count >0:
            raise RuntimeError("this function can not be called repeatly")
        model = None
        self.compute_model_count = 1
        while self.__pysat_sovlver.solve():
            self.compute_model_count += 1
            model = self.__pysat_sovlver.get_model()
            if self.__check(self.__formula.clauses, copy.deepcopy(model)):
                break
            positive_list=[]
            for item in model:
                if item >0:
                    positive_list.append(-item)
                else:
                    self.__pysat_sovlver.add_clause([item])
            self.__pysat_sovlver.add_clause(positive_list)
        return (model is not None ,model)

