import unittest
import random
from datetime import datetime
from jmetal.core.solution import BinarySolution
from nen.Problem import Problem, LP, QP
from nen.Solver.ExactWSOSolver import ExactWSOSolver
from nen.Solver.ExactWSOQPSolver import ExactWSOQPSolver


class ExactQPSolveTest(unittest.TestCase):
    # config
    LOOP_TIMES = 30

    def random_weights(self, objectives):
        weights = [random.randint(5, 100) for _ in range(len(objectives))]
        sum_weights = sum(weights)
        return [w / sum_weights for w in weights]

    def wso(self, objs, weights):
        return sum([objs[i] * weights[i] for i in range(len(objs))])

    def test_qp_solving(self) -> None:
        random.seed(datetime.now())
        for problem_name in ['Drupal', 'ms', 'rp', 'WebPortal']:
            # prepare problems
            problem = Problem(problem_name)
            problem.vectorize()
            lp = LP(problem_name, problem.objectives_order)
            qp = QP(problem_name, problem.objectives_order)
            # random weights
            for _ in range(ExactQPSolveTest.LOOP_TIMES):
                weights = self.random_weights(problem.objectives_order)
                ws = {problem.objectives_order[i]: weights[i] for i in range(problem.objectives_num)}
                lr = ExactWSOSolver.solve(lp, ws)
                qr = ExactWSOQPSolver.solve(qp, ws, 1e5)
                ls = lr.single
                qs = qr.single
                if ls is None and qs is None:
                    print('skipped')
                    continue
                elif ls is None or qs is None:
                    assert False
                else:
                    assert isinstance(ls, BinarySolution)
                    assert isinstance(qs, BinarySolution)
                    sl = self.wso(ls.objectives, weights)
                    sr = self.wso(qs.objectives, weights)
                    assert abs(sl - sr) < 1e-6, (sl, sr, ls.variables, qs.variables)
