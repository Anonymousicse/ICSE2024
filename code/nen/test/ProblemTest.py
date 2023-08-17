import unittest
from typing import List, Dict
import random
from datetime import datetime
from nen.Problem import Problem, LP, QP
from nen.util.util import FLOAT_PRECISION


class ProblemTest(unittest.TestCase):
    # configs
    LOOP_TIMES = 30

    def reset_seed(self) -> None:
        random.seed(datetime.now())

    def test_problem_load(self) -> None:
        problem_names = ['Amazon', 'BerkeleyDB', 'Drupal', 'ERS', 'WebPortal', 'ms', 'rp']
        for problem_name in problem_names:
            Problem(problem_name)
        empty_problem = Problem()
        another_problem = Problem('ms')
        empty_problem.clone(another_problem)
        assert empty_problem.name == another_problem.name
        assert empty_problem.variables == another_problem.variables
        assert empty_problem.objectives == another_problem.objectives
        assert len(empty_problem.constraints) == len(another_problem.constraints)

    def random_values(self, variables: List[str], num: int) -> List[Dict[str, bool]]:
        results = []
        for _ in range(num):
            results.append({k: True if random.randint(0, 1) == 1 else False for k in variables})
        return results

    def test_vectorize(self) -> None:
        self.reset_seed()
        problem_names = ['Amazon', 'BerkeleyDB', 'Drupal', 'ERS', 'WebPortal', 'ms', 'rp']
        for problem_name in problem_names:
            # load problem
            p = Problem(problem_name)
            # vectorize variables
            p.vectorize_variables()
            assert p.variables_index is not None
            assert len(p.variables_index) == len(p.variables)
            for v, i in p.variables_index.items():
                assert p.variables[i] == v
            # vectorize objectives
            objectives_order = list(p.objectives.keys())
            p.vectorize_objectives(objectives_order)
            assert len(p.objectives_index) == len(objectives_order)
            for objective_name in objectives_order:
                index = p.objectives_index[objective_name]
                for var in p.variables:
                    if var in p.objectives[objective_name]:
                        delta = p.objectives_matrix[p.variables_index[var], index] - p.objectives[objective_name][var]
                        assert abs(delta) < FLOAT_PRECISION
                    else:
                        assert abs(p.objectives_matrix[p.variables_index[var], index]) < FLOAT_PRECISION
            # generate some variable values for evaluation check
            for values in self.random_values(p.variables, ProblemTest.LOOP_TIMES):
                # vectorize values
                vector = p.vectorize_values(values)
                assert vector.shape[1] == len(p.variables)
                for var_index, var in enumerate(p.variables):
                    assert values[var] == vector[0, var_index]
                # evaluate
                obj_vec = vector @ p.objectives_matrix
                for obj_name in objectives_order:
                    obj = 0.0
                    for var, coef in p.objectives[obj_name].items():
                        if values[var]: obj += coef
                    assert abs(obj - obj_vec[0, p.objectives_index[obj_name]]) < FLOAT_PRECISION

    def same_list(self, l1: List[float], l2: List[float]) -> bool:
        if len(l1) != len(l2): return False
        for index in range(len(l1)):
            if abs(l1[index] - l2[index]) > FLOAT_PRECISION:
                return False
        return True

    def test_evaluate(self) -> None:
        self.reset_seed()
        problem_names = ['Amazon', 'BerkeleyDB', 'Drupal', 'ERS', 'WebPortal', 'ms', 'rp', 'make']
        for problem_name in problem_names:
            # load problem
            p = Problem(problem_name)
            # vectorize problem
            p.vectorize_variables()
            objectives_order = list(p.objectives.keys())
            p.vectorize_objectives(objectives_order)
            # generate some variable values for evaluation check
            for values in self.random_values(p.variables, ProblemTest.LOOP_TIMES):
                vector = p.vectorize_values(values)
                # evaluate objectives
                objs = p.evaluate_objectives(values)
                objs_ = (vector @ p.objectives_matrix).tolist()[0]
                assert self.same_list(objs, objs_)
                # evaluate constraints
                vlts = 0
                for cst in p.constraints:
                    if not cst.evaluate(values): vlts += 1
                violateds = p.evaluate_constraints(values, False)
                if vlts > 0: assert violateds == 1
                else: assert violateds == 0
                violateds = p.evaluate_constraints(values, True)
                assert violateds == vlts
                # evaluate together
                objs, violateds = p._evaluate(values)
                assert self.same_list(objs, objs_)
                assert violateds == vlts
                # evaluate to a BinarySolution
                bs = p.evaluate(values)
                assert len(bs.variables[0]) == len(p.variables)
                assert len(bs.variables[0]) == bs.number_of_variables
                assert len(bs.objectives) == bs.number_of_objectives
                assert len(bs.constraints) == 1
                for ind, val in enumerate(bs.variables[0]):
                    assert values[p.variables[ind]] == val
                assert self.same_list(objs, bs.objectives)
                assert violateds == bs.constraints[0]
                # evaluate with a new BinarySolution
                ns = p._empty_solution()
                ns.variables = [[]]
                for var in bs.variables[0]:
                    ns.variables[0].append(var)
                ns = p.evaluate_solution(ns)
                assert ns.variables == bs.variables
                assert ns.objectives == bs.objectives
                assert ns.constraints == bs.constraints

    def same_dict(self, d1: Dict[str, float], d2: Dict[str, float]) -> bool:
        if len(d1) != len(d2): return False
        for k, v in d1.items():
            if k not in d2: return False
            if abs(v - d2[k]) >= FLOAT_PRECISION: return False
        return True

    def test_weighted_objectives_sum(self) -> None:
        self.reset_seed()
        problem_names = ['Amazon', 'BerkeleyDB', 'Drupal', 'ERS', 'WebPortal', 'ms', 'rp', 'make']
        for problem_name in problem_names:
            p = Problem(problem_name)
            p.vectorize()
            weights = {}
            for obj_name in p.objectives_order:
                weights[obj_name] = random.random()
            single_obj = p.weighted_objectives_sum(weights)
            obj = {}
            for obj_name, wgt in weights.items():
                for k, v in p.objectives[obj_name].items():
                    if k not in obj: obj[k] = (wgt * v)
                    else: obj[k] += (wgt * v)
            assert self.same_dict(single_obj, obj), (single_obj, obj)
            assert self.same_dict(p.weighted_objectives_sum({k: 1 for k in weights}),
                                  p.weighted_objectives_sum())

    def test_lp_qp_initialize(self) -> None:
        problem_names = ['Amazon', 'BerkeleyDB', 'Drupal', 'ERS', 'WebPortal', 'ms', 'rp', 'make']
        for problem_name in problem_names:
            LP(problem_name)
            QP(problem_name)

