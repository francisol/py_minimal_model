import importlib
from inspect import isclass
from typing import Tuple

from pysat.formula import CNF


class Solver:
    """
        This class can  proxy a specific solver by solver's name or short name. \n
        The constructor need a   solver's name or short name ,other parameter will be given specific solver's constructor
    """

    def __init__(self, name='MM', mr=False, **kwargs):
        """
        This class can  proxy a specific solver by solver's name or short name. every solver use different algorithm
        The constructor need a solver's name or short name ,other parameters will be given specific solver's
        constructor

         Example:
        from minimal_model.solvers import Solver
        solver = Solver(name="MM",pysat_name="m22")
        solver.add_clause([1, 2])
        solver.add_clause([-2, 3])
        (sat,model) = solver.compute_minimal_model()
        print(sat)
        print(model)

        :param name : the algorithm's name MM or MR.
        :param mr : whether use mr  algorithm in every step
        :param kwargs : the parameters of the specific Solver's constructed function
        """
        module = importlib.import_module("minimal_model.solvers.mr_solvers" if mr else "minimal_model.solvers.solvers",
                                         self.__module__)
        self._real_solver = None
        for attr in dir(module):
            if not attr.startswith("_"):
                clz = getattr(module, attr)
                if isclass(clz) and hasattr(clz, 'names') and name in getattr(clz,
                                                                              'names'):
                    if mr:
                        if hasattr(clz, "mr") and getattr(clz, "mr"):
                            self._real_solver = clz(**kwargs)
                            break
                    else:
                        self._real_solver = clz(**kwargs)
                        break
        if self._real_solver is None:
            raise RuntimeError('no solver named [{}]'.format(name))
        print('compute minimal model use ', name)

    def compute_minimal_model(self) -> Tuple[bool, list]:
        """
        This method is used to  a minimal model,it will return a `tuple`.
        The first value means whether a CNF formula given to the solver is satisfiability
        The second value is a minimal model only if the formula is satisfiability, otherwise the value is None\n
        :return:  (satisfiability,minimal model)
        """
        return self._real_solver.compute_minimal_model()

    @property
    def formula(self) -> CNF:
        """
        get the original CNF formula
        """
        return self._real_solver.formula

    def add_clause(self, clause: list):
        """
        add clause to formula
        """
        self._real_solver.add_clause(clause)

    def append_formula(self, formula: CNF):
        """
        append formula to formula
        """
        self._real_solver.append_formula(formula)

    def print_status(self):
        return self._real_solver.print_status()

    @property
    def compute_model_count(self) -> int:
        return self._real_solver.compute_model_count

    @property
    def cpu_time(self) -> int:
        """
        get the cpu time of solving minimal model
        """
        return self._real_solver.cpu_time
