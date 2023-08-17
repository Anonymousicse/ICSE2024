from typing import Dict
from nen.Problem import LP
from nen.Result import Result
from nen.Solver.MetaSolver import SolverUtil, ExactSolver


class ExactWSOSolver:
    """ExactWSOSolver [summary] ExactWSOSOlver is an exact solver using cplex,
    handling multi-objective problem with weighted sum objective technique.
    """
    @staticmethod
    def solve(problem: LP, weights: Dict[str, float]) -> Result:
        """solve [summary] solve the LP with given weights, record results in result parameter.
        """
        # weighted sum objective
        wso = SolverUtil.weighted_sum_objective(problem.objectives, weights)
        # prepare solver
        solver = ExactSolver.initialized_cplex_solver(problem)
        ExactSolver.set_minimizing_objective(solver, wso)
        # solve
        start = SolverUtil.time()
        values = ExactSolver.solve_and_get_values(solver, problem.variables)
        end = SolverUtil.time()
        # prepare result
        result = Result(problem)
        if values != {}:
            result.add(problem.evaluate(values))
            result.elapsed = end - start
        result.info['weights'] = weights
        return result
