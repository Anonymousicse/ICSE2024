from typing import List, Tuple, Dict
from jmetal.core.solution import BinarySolution
from nen.Problem import LP
from nen.Term import Linear
from nen.Result import Result
from nen.Solver.MetaSolver import ExactSolver, SolverUtil


class SolRep3DSolver:
    """ [summary] SolRep3D is a sampling-based exact solver, aim at finding distributed evenly non-dominated solutions
    of tri-objective optimization problem.
    """
    @staticmethod
    def solve_one_dimension(problem: LP, objective_index: int) -> BinarySolution:
        """solve_one_dimension [summary] solve the problem with a certain objective denoted by its index,
        return the solution.
        """
        solver = ExactSolver.initialized_cplex_solver(problem)
        objective_name = problem.objectives_order[objective_index]
        ExactSolver.set_minimizing_objective(solver, problem.objectives[objective_name])
        values = ExactSolver.solve_and_get_values(solver, problem.variables)
        return problem.evaluate(values)
    
    @staticmethod
    def solve4D(problem: LP, sampling_size: int) -> Result:
        """solve [summary] solve linear programming problem and save results in result.
        """
        # find the anchors
        anchor_1 = SolRep3DSolver.solve_one_dimension(problem, 1)
        anchor_2 = SolRep3DSolver.solve_one_dimension(problem, 2)
        anchor_3 = SolRep3DSolver.solve_one_dimension(problem, 3)
        assert anchor_1.variables[0] != anchor_2.variables[0], 'please change the objective order'
        assert anchor_2.variables[0] != anchor_3.variables[0], 'please change the objective order'
        # sampling from the utopia plane (a line from anchor_1 to anchor_2, actually)
        step_1 = (anchor_2.objectives[1] - anchor_1.objectives[1]) / sampling_size
        step_2 = (anchor_3.objectives[2] - anchor_1.objectives[2]) / sampling_size
        step_3 = (anchor_3.objectives[3] - anchor_2.objectives[3]) / sampling_size
        rhs_1, rhs_2, rhs_3 = anchor_1.objectives[1], anchor_1.objectives[2], anchor_1.objectives[3]
        points: List[Tuple[float, float, float]] = []
        for _ in range(sampling_size - 1):
            points.append((rhs_1, rhs_2, rhs_3))
            rhs_1 += step_1
            rhs_2 += step_2
            rhs_3 += step_3
        points.append((rhs_1, rhs_2, rhs_3))
        # initialize the solver
        solver = ExactSolver.initialized_cplex_solver(problem)
        # set obj[1] and obj[2] as constraints
        obj_1, obj_2, obj_3 = problem.objectives_order[1], problem.objectives_order[2], problem.objectives_order[3]
        ExactSolver.add_constraint(solver, obj_1, Linear(problem.objectives[obj_1], '<=', 0.0))
        ExactSolver.add_constraint(solver, obj_2, Linear(problem.objectives[obj_2], '<=', 0.0))
        ExactSolver.add_constraint(solver, obj_3, Linear(problem.objectives[obj_3], '<=', 0.0))
        # set objective
        obj_0 = problem.objectives_order[0]
        ExactSolver.set_minimizing_objective(solver, problem.objectives[obj_0])
        start = SolverUtil.time()
        values_list: List[Dict[str, bool]] = []
        for rhs_1, rhs_2, rhs_3 in points:
            ExactSolver.set_constraint_rhs(solver, obj_1, rhs_1)
            ExactSolver.set_constraint_rhs(solver, obj_2, rhs_2)
            ExactSolver.set_constraint_rhs(solver, obj_3, rhs_3)
            values = ExactSolver.solve_and_get_values(solver, problem.variables)
            if len(values) > 0: values_list.append(values)
        end = SolverUtil.time()
        # collect results
        result = Result(problem)
        for values in values_list:
            result.add(problem.evaluate(values))
        result.elapsed = end - start
        return result

    @staticmethod
    def solve3D(problem: LP, sampling_size: int) -> Result:
        """solve [summary] solve linear programming problem and save results in result.
        """
        # check sampling size >= 2
        assert sampling_size >= 2
        # check whether three objectives
        assert len(problem.objectives_order) == 3
        # find the anchors
        anchor_1 = SolRep3DSolver.solve_one_dimension(problem, 1)
        anchor_2 = SolRep3DSolver.solve_one_dimension(problem, 2)
        assert anchor_1.variables[0] != anchor_2.variables[0], 'please change the objective order'
        # sampling from the utopia plane (a line from anchor_1 to anchor_2, actually)
        step_1 = (anchor_2.objectives[1] - anchor_1.objectives[1]) / sampling_size
        step_2 = (anchor_2.objectives[2] - anchor_1.objectives[2]) / sampling_size
        rhs_1, rhs_2 = anchor_1.objectives[1], anchor_1.objectives[2]
        points: List[Tuple[float, float]] = []
        for _ in range(sampling_size - 1):
            points.append((rhs_1, rhs_2))
            rhs_1 += step_1
            rhs_2 += step_2
        points.append((rhs_1, rhs_2))
        # initialize the solver
        solver = ExactSolver.initialized_cplex_solver(problem)
        # set obj[1] and obj[2] as constraints
        obj_1, obj_2 = problem.objectives_order[1], problem.objectives_order[2]
        ExactSolver.add_constraint(solver, obj_1, Linear(problem.objectives[obj_1], '<=', 0.0))
        ExactSolver.add_constraint(solver, obj_2, Linear(problem.objectives[obj_2], '<=', 0.0))
        # set objective
        obj_0 = problem.objectives_order[0]
        ExactSolver.set_minimizing_objective(solver, problem.objectives[obj_0])
        start = SolverUtil.time()
        values_list: List[Dict[str, bool]] = []
        for rhs_1, rhs_2 in points:
            ExactSolver.set_constraint_rhs(solver, obj_1, rhs_1)
            ExactSolver.set_constraint_rhs(solver, obj_2, rhs_2)
            values = ExactSolver.solve_and_get_values(solver, problem.variables)
            if len(values) > 0: values_list.append(values)
        end = SolverUtil.time()
        # collect results
        result = Result(problem)
        for values in values_list:
            result.add(problem.evaluate(values))
        result.elapsed = end - start
        return result