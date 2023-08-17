from nen.Problem import LP
from nen.Result import Result
from nen.Solver.MetaSolver import ExactSolver


class ExactECSolver:
    """ [summary] ExactECSolver is a multi-objective solver applied with epsilon-constrain technique.
    """
    @staticmethod
    def solve(problem: LP) -> Result:
        """solve [summary] solve linear programming problem and save results in result.
        """
        archive, elapsed = ExactSolver.epsilon_constraint(problem, 1)
        result = Result(problem)
        result.set_solution_list(archive.solution_list)
        result.elapsed = elapsed
        result.total_num_anneals = len(result.solution_list)
        return result
