import unittest
from typing import Dict, List
import random
from datetime import datetime
from cplex import SparsePair
from nen.Solver.MetaSolver import SolverUtil, ExactSolver
from nen.Term import Linear
from nen.util.util import FLOAT_PRECISION
from nen.Problem import LP


class UtilTest(unittest.TestCase):
    LOOP_TIMES = 100
    VAR_NUM = 50
    EMPTY_RATIO = 0.5

    def reset_seed(self) -> None:
        random.seed(datetime.now())

    def random_objectives(self, num: int) -> Dict[str, Dict[str, float]]:
        objs: Dict[str, Dict[str, float]] = {}
        for i in range(num):
            name = '#{}'.format(i)
            objs[name] = {}
            for j in range(UtilTest.VAR_NUM):
                if random.random() < UtilTest.EMPTY_RATIO: continue
                objs[name]['x{}'.format(j)] = random.random()
        return objs

    def same_float_dict(self, d1: Dict[str, float], d2: Dict[str, float]) -> bool:
        if set(d1.keys()) != set(d2.keys()): return False
        for k in d1:
            if abs(d1[k] - d2[k]) >= FLOAT_PRECISION:
                return False
        return True

    def test_wso_operations(self) -> None:
        self.reset_seed()
        for _ in range(UtilTest.LOOP_TIMES):
            # random objectives
            objs = self.random_objectives(5)
            # random weights
            weights: Dict[str, float] = {k: random.random() for k in objs}
            # wso
            the_obj = SolverUtil.weighted_sum_objective(objs, weights)
            # check
            obj_: Dict[str, float] = {}
            for obj_name, obj in objs.items():
                w = weights[obj_name]
                for k, v in obj.items():
                    if k not in obj_:
                        obj_[k] = w * v
                    else:
                        obj_[k] += w * v
            assert self.same_float_dict(the_obj, obj_)

    def spair_pair_to_coef_dict(self, sp: SparsePair, variables: List[str]) -> Dict[str, float]:
        coef: Dict[str, float] = {}
        for i, var_index in enumerate(sp.ind):
            coef[variables[var_index]] = sp.val[i]
        return coef

    def test_objective_theoretical_boundary(self) -> None:
        for _ in range(UtilTest.LOOP_TIMES):
            obj = list(self.random_objectives(1).values())[0]
            for k in obj: obj[k] -= 0.5
            lb_ = sum([v for v in obj.values() if v < 0])
            ub_ = sum([v for v in obj.values() if v > 0])
            (lb, ub) = SolverUtil.objective_theoretical_boundary(obj)
            assert abs(lb_ - lb) < FLOAT_PRECISION
            assert abs(ub_ - ub) < FLOAT_PRECISION

    def test_cplex_initialized(self) -> None:
        problem_names = ['Drupal', 'make', 'ms', 'rp', 'WebPortal']
        for problem_name in problem_names:
            p = LP(problem_name)
            s = ExactSolver(p)
            # check variables
            assert s.solver.variables.get_names() == p.variables
            assert s.solver.variables.get_types() == ['B'] * p.variables_num
            # check constraints
            assert len(s.solver.linear_constraints.get_names()) == len(p.constraints_lp)
            for i, lp in enumerate(p.constraints_lp):
                assert self.same_float_dict(
                    self.spair_pair_to_coef_dict(s.solver.linear_constraints.get_rows(i), p.variables),
                    lp.coef)
                assert s.solver.linear_constraints.get_senses('c{}'.format(i)) == 'L' if lp.sense == '<=' else 'E'
                assert abs(s.solver.linear_constraints.get_rhs('c{}'.format(i)) - lp.rhs) < FLOAT_PRECISION

    def test_other_cplex_involved_operations(self) -> None:
        problem_names = ['Drupal', 'make', 'ms', 'rp', 'WebPortal']
        for problem_name in problem_names:
            p = LP(problem_name)
            s = ExactSolver.initialized_cplex_solver(p)
            # add constraint
            ExactSolver.add_constraint(s, 'tmp', Linear({var: 1.0 for var in p.variables}, '<=', 0.0))
            assert s.linear_constraints.get_senses('tmp') == 'L'
            assert abs(s.linear_constraints.get_rhs('tmp') - 0.0) < FLOAT_PRECISION
            ExactSolver.set_constraint_rhs(s, 'tmp', 3.0)
            assert abs(s.linear_constraints.get_rhs('tmp') - 3.0) < FLOAT_PRECISION
            ExactSolver.set_constraint_rhs(s, 'tmp', 4.999)
            assert abs(s.linear_constraints.get_rhs('tmp') - 4.999) < FLOAT_PRECISION
