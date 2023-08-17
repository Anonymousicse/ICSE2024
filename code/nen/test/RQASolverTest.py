import unittest
import random
from datetime import datetime
from jmetal.core.solution import BinarySolution

from nen import Quadratic
from nen.Problem import Problem, LP, QP
from nen.Solver import EmbeddingSampler, SolverUtil
from nen.Solver.RQAWSOSolver import RQAWSOSolver


class RQASolveTest(unittest.TestCase):
    # config
    LOOP_TIMES = 30

    def random_weights(self, objectives):
        weights = [random.randint(5, 100) for _ in range(len(objectives))]
        sum_weights = sum(weights)
        return [w / sum_weights for w in weights]

    def caculate_wso(self, objs, weights):
        return sum([objs[i] * weights[i] for i in range(len(objs))])

    def caculate_penalty(self, wso, qp):
        penalty = EmbeddingSampler.calculate_penalty(wso, qp.constraint_sum)
        return penalty

    def test_qp_solving(self) -> None:
        random.seed(datetime.now())
        for problem_name in ['rp']:
            # prepare problems
            problem = Problem(problem_name)
            problem.vectorize()
            qp = QP(problem_name, problem.objectives_order)

            # random weights
            for _ in range(RQASolveTest.LOOP_TIMES):
                weights = self.random_weights(problem.objectives_order)
                ws = {problem.objectives_order[i]: weights[i] for i in range(problem.objectives_num)}
                wso = Quadratic(linear=SolverUtil.weighted_sum_objective(problem.objectives, ws))
                penalty = self.caculate_penalty(wso, qp)
                anneal_schedule = [[0.0, 1.0], [10.0, 0.5], [20, 1.0]]
                rqaw = RQAWSOSolver.solve(qp, ws, penalty, self.LOOP_TIMES, anneal_schedule, 1)
                rqa = rqaw.single
                assert isinstance(rqa, Optional[BinarySolution])

