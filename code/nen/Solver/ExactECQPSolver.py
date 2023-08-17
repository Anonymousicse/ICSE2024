from typing import List, Dict, Tuple, Union
import copy
import time
from math import floor, ceil
from nen.Term import Constraint, Quadratic
from nen.Problem import QP
from nen.Result import NDArchive, Result
from nen.Solver.MetaSolver import ExactSolver, SolverUtil


class ExactECQPSolver:
    """ [summary] ExactECQPSolver is an exact solver for solving MOQP in a epsilon constraint way.
    """
    @staticmethod
    def reduced_problem(problem: QP, selected_objective: str, reduced_objectives: List[str],
                        objectives_rhs: List[float], penalty: float
                        ) -> Tuple[Quadratic, List[str]]:
        """reduced_problem [summary] reduce MO QP to a single Quadratic for optimization.
        Given a selected_objective as the final objective, other reduced_objectives are converted
        into a linear inequation and further converted as a part of quadratic via their rhs.
        penalty is for selected_objective + penalty * constraint.

        It would return a Quadratic for optimization and a list of variables.
        """
        # prepare the objective
        objective: Quadratic = Quadratic(linear=problem.objectives[selected_objective])
        # prepare the objectives constraints
        objectives_constraints = \
            [Constraint(problem.objectives[name], '<=', objectives_rhs[ind])
             for ind, name in enumerate(reduced_objectives)]
        additional_constraints: List[Quadratic] = []
        variables = copy.copy(problem.artificial_list)
        # convert to quadratic form
        for constraint in objectives_constraints:
            additional_constraints.append(constraint.to_quadratic(variables))
        # collect all constraints and sum up
        all_constraint = Constraint.quadratic_sum(problem.constraints_qp + additional_constraints)
        quadratic = Constraint.quadratic_weighted_add(1, penalty, objective, all_constraint)
        return (quadratic, problem.variables + variables)

    @staticmethod
    def next_rhs(objectives_rhs: List[float], step: int,
                 objectives_boundaries: List[Tuple[float, float]]) -> Union[List[float], None]:
        """next_rhs [summary] from the current rhs state to find the next state, None if no next state.
        """
        for i in range(len(objectives_rhs) - 1, -1, -1):
            if objectives_rhs[i] - step <= objectives_boundaries[i][0]:
                objectives_rhs[i] = objectives_boundaries[i][1]
            else:
                objectives_rhs[i] -= step
                return objectives_rhs
        return None

    @staticmethod
    def solve_once(quadratic: Quadratic, problem_variables: List[str],
                   all_variables: List[str]) -> Dict[str, bool]:
        # prepare the solver
        solver = ExactSolver.variables_initialized_cplex_solver(all_variables)
        ExactSolver.set_minimizing_qudratic_objective(solver, quadratic)
        # solve
        return ExactSolver.solve_and_get_values(solver, problem_variables)

    @staticmethod
    def epsilon_constraint(problem: QP, step: int, penalty: float) -> Tuple[NDArchive, float]:
        """epsilon_constraint [summary] solve qp problem with multi-objective, applied with epsilon-constraint.
        """
        # Note that the first objective is the selected objective, others are being reduced.
        # calculate theoretical boundaries of objectives[1:] and add constraint into solver
        reduced_names: List[str] = []
        boundaries: List[Tuple[float, float]] = []
        for obj_name in problem.objectives_order[1:]:
            obj = problem.objectives[obj_name]
            reduced_names.append(obj_name)
            (lb, ub) = SolverUtil.objective_theoretical_boundary(obj)
            boundaries.append((floor(lb), ceil(ub)))
        # prepare a values list
        values_list: List[Dict[str, bool]] = []
        # prepare rhs, initialized with the upper bounds
        rhs: Union[List[float], None] = [b[1] for b in boundaries]
        start = time.perf_counter()
        while rhs is not None:
            # prepare the problem
            quadratic, variables = \
                ExactECQPSolver.reduced_problem(problem, problem.objectives_order[0],
                                                problem.objectives_order[1:], rhs, penalty)
            # solve
            values = ExactECQPSolver.solve_once(quadratic, problem.variables, variables)
            if values != {}: values_list.append(values)
            # update the rhs
            rhs = ExactECQPSolver.next_rhs(rhs, step, boundaries)
        end = time.perf_counter()
        # prepare an archive
        archive = NDArchive(problem.variables_num, problem.objectives_num)
        # evaluate solutions and add into archive
        for values in values_list:
            archive.add(problem.evaluate(values))
        # return
        return (archive, end - start)

    @staticmethod
    def solve(problem: QP, step: int, penalty: float) -> None:
        """solve [summary] solve qp problem with multi-objective, applied with epsilon-constraint.
        """
        archive, elapsed = ExactECQPSolver.epsilon_constraint(problem, step, penalty)
        result = Result(problem)
        result.set_solution_list(archive.solution_list)
        result.elapsed = elapsed
        return result
