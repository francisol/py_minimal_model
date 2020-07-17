# minimal_model

The package based on `python-sat`  provides  a library and a cli tool to compute minimal model of a CNF formula.

**WARNING**: The package can't support python2

## Dependencies

- python-sat :A toolkit for SAT-based prototyping in Python
- psutil : Cross-platform lib for process and system monitoring in Python.

## Algorithm
There are two algorithms can be used to compute minimal model
### MM
### MR

## Usage
### library
```python
>>> from minimal_model.solvers import Solver
>>> solver = Solver(name="MM",pysat_name="m22")
>>> solver.add_clause([1, 2])
>>> solver.add_clause([-2, 3])
>>> (sat,model) = solver.compute_minimal_model()
>>> print(sat)
>>> print(model)
...
True
[1, -2, -3]
```

### cli
use `--help` to get usage
```bash
minimal_model --help
```
```
usage: minimal_model [-h] --file FILE [--pysat PYSAT] [--mem-limit MEM_LIMIT]
                     [--time-limit TIME_LIMIT] [--mod {MR,MM}]
                     [--simpfy SIMPFY]

A cli to compute a minimal model given by argument

optional arguments:
  -h, --help            show this help message and exit
  --file FILE           The path of CNF file
  --pysat PYSAT         The solver name of pysat, the cli will depend it，you can select followed options
                            cadical     = ('cd', 'cdl', 'cadical')
                            glucose3    = ('g3', 'g30', 'glucose3', 'glucose30')
                            glucose4    = ('g4', 'g41', 'glucose4', 'glucose41')
                            lingeling   = ('lgl', 'lingeling')
                            maplechrono = ('mcb', 'chrono', 'maplechrono')
                            maplecm     = ('mcm', 'maplecm')
                            maplesat    = ('mpl', 'maple', 'maplesat')
                            minicard    = ('mc', 'mcard', 'minicard')
                            minisat22   = ('m22', 'msat22', 'minisat22')
                            minisatgh   = ('mgh', 'msat-gh', 'minisat-gh')
                            
  --mem-limit MEM_LIMIT
                        Limit on memory usage in megabytes. zero is unlimited
  --time-limit TIME_LIMIT
                        Limit on CPU time allowed in seconds.zero is unlimited
  --mod {MR,MM}         Select a algorithm use to compute minimal model
  --simpfy SIMPFY       If it true cli will print minimal model only value is positive
```
## Installation

```bash
git clone https://github.com/francisol/py_minimal_model.git
cd py_minimal_model
python ./setup.py install
```