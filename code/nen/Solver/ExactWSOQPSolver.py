from typing import Dict
from nen.Problem import QP
from nen.Term import Constraint, Quadratic
from nen.Result import Result
from nen.Solver.MetaSolver import SolverUtil, ExactSolver


class ExactWSOQPSolver:
    """ExactWSOQPSolver [summary] ExactWSOQPSOlver is an exact solver using cplex,
    handling multi-objective quadratic programming problem with weighted sum objective technique.
    """
    @staticmethod
    def solve(problem: QP, weights: Dict[str, float], penalty: float) -> Result:
        """solve [summary] solve the QP with given weights, return result.
        """
        # weighted sum objective
        wso = SolverUtil.weighted_sum_objective(problem.objectives, weights)
        # add constraints to objective with penalty
        objective = Constraint.quadratic_weighted_add(1, penalty, Quadratic(linear=wso), problem.constraint_sum)
        # prepare solver
        solver = ExactSolver.variables_initialized_cplex_solver(problem.variables + problem.artificial_list)
        ExactSolver.set_minimizing_qudratic_objective(solver, objective)
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
        result.info['penalty'] = penalty
        return result
