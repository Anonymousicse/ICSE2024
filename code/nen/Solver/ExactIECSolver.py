from typing import List
from jmetal.core.solution import BinarySolution
from nen.Problem import LP
from nen.Term import Linear
from nen.Result import Result
from nen.Solver.MetaSolver import ExactSolver, SolverUtil


class ExactIECSolver:
    """ [summary] ExactIECSolver is a bi-objective solver applied with epsilon-constrain technique.
    It improves EC with update rhs by the last solutions solved.
    """
    @staticmethod
    def solve(problem: LP) -> Result:
        """solve [summary] solve linear programming problem and save results in result.
        """
        # check whether two objectives
        assert len(problem.objectives_order) == 2
        # initialize the solver
        solver = ExactSolver.initialized_cplex_solver(problem)
        # convert the second objective as a constraint
        second_objective_name = problem.objectives_order[1]
        second_objective = problem.objectives[second_objective_name]
        lb, ub = SolverUtil.objective_theoretical_boundary(second_objective)
        ExactSolver.add_constraint(solver, second_objective_name, Linear(second_objective, '<=', 0.0))
        # set objectives
        ExactSolver.set_minimizing_objective(solver, problem.objectives[problem.objectives_order[0]])
        # solve
        solution_list: List[BinarySolution] = []
        start = SolverUtil.time()
        rhs = ub
        while rhs >= lb:
            # set rhs and solve
            ExactSolver.set_constraint_rhs(solver, second_objective_name, rhs)
            values = ExactSolver.solve_and_get_values(solver, problem.variables)
            if values == {}:
                rhs -= 1
            else:
                solution = problem.evaluate(values)
                assert solution.objectives[1] <= rhs
                rhs = solution.objectives[1] - 1
                solution_list.append(solution)
        end = SolverUtil.time()
        # prepare archive
        result = Result(problem)
        for solution in solution_list:
            result.add(solution)
        result.elapsed = end - start
        return result
