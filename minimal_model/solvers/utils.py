from typing import List

from minimal_model.graph import Graph


def mr(clauses, model) -> List[List[int]]:
    """
    minimal reduce algorithm
    """
    # positive_model = set([x for x in model if x > 0])
    negative_model = {x for x in model if x < 0}
    result = []
    for clause in clauses:
        # header = [x for x in clause if x > 0]
        body = {x for x in clause if x < 0}
        if body.intersection(negative_model):
            continue
        c = [x for x in clause if - x not in negative_model]
        if c:
            result.append(c)
    return result


def create_graph(clauses, formula_nv) -> Graph:
    """
    create dependency graph
    """
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


def reduce(clauses, s) -> List[List[int]]:
    """
    reduce clauses by s
    :return: new clauses
    """
    for clause in clauses:
        header = {x for x in clause if x > 0}
        if header.intersection(s):
            clause.clear()
            continue
        c = [x for x in clause if abs(x) not in s]
        clause.clear()
        clause.extend(c)
    return list(filter(None, clauses))


def compute_ts(clauses, weights, formula_nv) -> dict:
    ts = {}
    key = formula_nv
    for clause in clauses:
        c = {abs(x) for x in clause}
        if c.issubset(weights) and clause:
            ts[key] = clause
        key += 1
    return ts


def compute_s(component, limit):
    return {x for x in component if x <= limit}
