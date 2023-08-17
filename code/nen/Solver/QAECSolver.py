from typing import List, Dict, Tuple
from copy import copy
from nen.Term import Quadratic, Constraint
from nen.Problem import QP
from nen.Result import Result
from nen.Solver.MetaSolver import SolverUtil
from nen.Solver.EmbeddingSampler import EmbeddingSampler


class QAECSolver:
    """ [summary] QAECSolver adopts Epsilon-Constraint based Multi-Objective decompostion,
    aiming at MOO.

    It looks like CWMOIP rather than epsilon-constraint.
    """
    @staticmethod
    def solve(problem: QP, sample_per_dim: int, num_reads: int) -> Result:
        # calculate the cwmoip like objective
        objectives = [problem.objectives[name] for name in problem.objectives_order]
        boundaries = [SolverUtil.objective_theoretical_boundary(obj) for obj in objectives]
        objective = QAECSolver.cwmoip_objective(objectives, boundaries)
        # get the constraint sum
        constraint_sum = problem.constraint_sum
        # get the bound constraints
        bound_constraints = [Constraint(left=objectives[i], sense='<=') for i in range(1, len(objectives))]
        # solve
        k = len(objectives) - 1
        return QAECSolver.epsilon_constraint(objective, constraint_sum, bound_constraints,
                                             boundaries, sample_per_dim, problem, k, num_reads)

    @staticmethod
    def cwmoip_objective(objectives: List[Dict[str, float]], boundaries: List[Tuple[float, float]]) -> Quadratic:
        """cwmoip_objective [summary] calculate cwmoip style objective.

        For (F1, ..., Fk), return F1 + w2(F2 + w3(F3 + ...)), wi is 1 / (up(Fi) - low(Fi) + 1).
        """
        n = len(objectives)
        # calculate weights
        weights = [1.0] * n
        for index in range(1, n):
            lb, ub = boundaries[index]
            weights[index] = weights[index - 1] * (1 / (ub - lb + 1.0))
        # add up objectives
        objective: Dict[str, float] = {}
        for index in range(n):
            w = weights[index]
            for k, v in objectives[index].items():
                if k in objective:
                    objective[k] += (w * v)
                else:
                    objective[k] = (w * v)
        return Quadratic(linear=objective)

    @staticmethod
    def cwmoip_update_rhs(k: int, result: Result) -> int:
        """update_rhs [summary] return max(F(s)) - 1, for all s in result.
        """
        return max([s.objectives[k] for s in result.solution_list]) - 1

    @staticmethod
    def epsilon_constraint(objective: Quadratic, constraint_sum: Quadratic, bound_constraints: List[Constraint],
                           boundaries: List[Tuple[float, float]], sample_per_dim: int,
                           problem: QP, k: int, num_reads: int) -> Result:
        """epsilon_constraint [summary] recurse solve MOO by epsilon-constraint,
        update bound w.r.t to sample_per_dim and boundaries.
        """
        # k == 0: solve, k > 0: reduce objective
        if k == 0:
            result = Result(problem)
            # prepare the objective and the sum of constraints
            t1 = SolverUtil.time()
            artificial_list = copy(problem.artificial_list)
            constraints = [constraint_sum] + [cst.to_quadratic(artificial_list) for cst in bound_constraints]
            constraint = Constraint.quadratic_sum(constraints)
            # calculate the penalty
            p = EmbeddingSampler.calculate_penalty(objective, constraint)
            qubo = Constraint.quadratic_to_qubo_dict(Constraint.quadratic_weighted_add(1.0, p, objective, constraint))
            # sample
            sampler = EmbeddingSampler()
            result.elapsed += (SolverUtil.time() - t1)
            sampleset, qpu_elapsed = sampler.sample(qubo, num_reads=num_reads)
            result.elapsed += qpu_elapsed
            # postprocess
            t2 = SolverUtil.time()
            for values in EmbeddingSampler.get_values(sampleset, problem.variables):
                solution = problem.evaluate(values)
                if sum(solution.constraints) == 0:
                    result.add(solution)
            result.elapsed += (SolverUtil.time() - t2)
            return result
        else:
            result = Result(problem)
            # iterate the boundary of the k-th objective
            lb, ub = boundaries[k - 1]
            step = (ub - lb) / sample_per_dim
            rhs = ub
            while rhs > lb:
                # update the k-th bound constraint
                bound_constraints[k - 1].right = rhs
                sub_result = QAECSolver.epsilon_constraint(objective, constraint_sum, bound_constraints,
                                                           boundaries, sample_per_dim,
                                                           problem, k - 1, num_reads)
                result.elapsed += sub_result.elapsed
                # update rhs and collect the sub-result solutions
                t3 = SolverUtil.time()
                rhs -= step
                for solution in sub_result.solution_list:
                    result.add(solution)
                result.elapsed += (SolverUtil.time() - t3)
            return result
