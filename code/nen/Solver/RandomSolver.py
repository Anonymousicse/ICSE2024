from typing import Union, Dict, List, Callable
import random
import datetime
import copy
from nen.Problem import Problem, LP, QP
from nen.Result import Result
from nen.Solver.MetaSolver import SolverUtil


ProblemType = Union[Problem, LP, QP]


class SolutionGenerator:
    """ [summary] It contains serveral generators for variables distribution.
    """
    @staticmethod
    def uniform_iid_generator(values: Dict[str, bool]) -> Dict[str, bool]:
        """uniform_iid_generator [summary] variables are idd. and subject to uniform distribution,
        which is p(0) = p(1) = 1/2.
        """
        for var in values:
            values[var] = (random.randint(0, 1) == 1)
        return values

    @staticmethod
    def binomial_id_generator(values: Dict[str, bool], distribution: Dict[str, float]) -> Dict[str, bool]:
        """binomial_id_generator [summary] variables are all independent and subject to a binomial distribution,
        which is p(var = 1) = distribution[var].
        """
        for var in values:
            values[var] = (random.random() > distribution[var])
        return values


class RandomSolver:
    """ [summary] RandomSolver, randomly generate solutions for comparison.
    """
    @staticmethod
    def solve(problem: Problem, generate_times: int,
              generator: Callable[[Dict[str, bool]], Dict[str, bool]] = SolutionGenerator.uniform_iid_generator
              ) -> Result:
        random.seed(datetime.datetime.now())
        # prepare values
        values: Dict[str, bool] = {var: False for var in problem.variables}
        values_list: List[Dict[str, bool]] = []
        start = SolverUtil.time()
        for _ in range(generate_times):
            values = generator(values)
            if values != {}: values_list.append(copy.copy(values))
        end = SolverUtil.time()
        # prepare archive
        result = Result(problem)
        for vals in values_list:
            # evaluate and add in archive
            result.add(problem.evaluate(vals))
        result.elapsed = end - start
        result.info['generate_times'] = generate_times
        return result
