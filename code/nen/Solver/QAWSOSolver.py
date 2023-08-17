from typing import Dict, List, Union
from jmetal.core.solution import BinarySolution
from nen.Term import Constraint, Quadratic
from nen.Problem import QP
from nen.Result import Result, NDArchive
from nen.Solver.MetaSolver import SolverUtil
from nen.Solver.EmbeddingSampler import EmbeddingSampler
from greedy import SteepestDescentSolver
from dimod.binary_quadratic_model import BinaryQuadraticModel


class QAWSOSolver:
    """ [summary] QAWSOSolver, stands for Quantum Annealling Weighted Sum Objective Solver.

    The Quantum Annealling Solver is implemeneted with D-Wave Leap,
    make sure the environment is configured successfully accordingly.
    """
    @staticmethod
    def solve_best(problem: QP, weights: Dict[str, float], penalty: float, num_reads: int, iterations: int, postprocess: bool = False) -> Result:
        """solve [summary] solve single objective qp (applied wso technique), return Result.
        """
        print("start SOQA to solve {}".format(problem.name))
        # prepare wso objective
        wso = SolverUtil.weighted_sum_objective(problem.objectives, weights)
        # add constraints to objective with penalty
        objective = Constraint.quadratic_weighted_add(1, penalty, Quadratic(linear=wso), problem.constraint_sum)
        qubo = Constraint.quadratic_to_qubo_dict(objective)
        bqm = BinaryQuadraticModel.from_qubo(qubo)
        result = Result(problem)
        # Solve in QA
        elapseds = 0.0
        for _ in range(iterations):
            solution_list: List[BinarySolution] = []
            sampler = EmbeddingSampler()
            # sampleset, elapsed = sampler.sample(qubo, num_reads=num_reads, answer_mode='raw', postprocess='sampling')
            raw_sampleset, elapsed = sampler.sample(qubo, num_reads=num_reads, answer_mode='raw')
            
            # get results
            count_feasible = 0
            for values, occurrence in EmbeddingSampler.get_values_and_occurrence(raw_sampleset, problem.variables):
                solution = problem.evaluate(values)
                solution_list.append(solution)
                if solution.constraints[0] == 0:
                    count_feasible += 1
            if count_feasible == 0 or postprocess:
                local_solver = SteepestDescentSolver()
                sampleset = local_solver.sample(bqm=bqm, initial_states=raw_sampleset)
                solution_list = []
                for values, occurrence in EmbeddingSampler.get_values_and_occurrence(sampleset, problem.variables):
                    solution = problem.evaluate(values)
                    solution_list.append(solution)
            res = QAWSOSolver.best_solution(solution_list, problem, weights)
            result.wso_add(res)
            elapseds += elapsed
        result.elapsed = elapseds
        
        # storage parameters
        result.info['weights'] = weights
        result.info['penalty'] = penalty
        result.info['num_reads'] = num_reads
        result.total_num_anneals = iterations * num_reads
        print("end SOQA to solve")
        return result
    
    def solve(problem: QP, weights: Dict[str, float], penalty: float, num_reads: int) -> Result:
        """solve [summary] solve single objective qp (applied wso technique), return Result.
        """
        print("start SOQA to solve {}".format(problem.name))
        # prepare wso objective
        wso = SolverUtil.weighted_sum_objective(problem.objectives, weights)
        # add constraints to objective with penalty
        objective = Constraint.quadratic_weighted_add(1, penalty, Quadratic(linear=wso), problem.constraint_sum)
        qubo = Constraint.quadratic_to_qubo_dict(objective)
        result = Result(problem)
        # Solve in QA
        sampler = EmbeddingSampler()
        sampleset, elapsed = sampler.sample(qubo, num_reads=num_reads, answer_mode='raw')
        # get results
        for values, occurrence in EmbeddingSampler.get_values_and_occurrence(sampleset, problem.variables):
            solution = problem.evaluate(values)
            result.wso_add(solution)

        result.elapsed = elapsed
        
        # storage parameters
        result.info['weights'] = weights
        result.info['penalty'] = penalty
        result.info['num_reads'] = num_reads
        print("end SOQA to solve")
        return result

    @staticmethod
    def best_solution(solution_list: List[BinarySolution],
                      problem: QP, weights: Dict[str, float]) -> Union[None, BinarySolution]:
        """best_solution [summary] get the best solution from the archive with certain weights.
        """
        best_value: float = float('inf')
        best_solution: Union[None, BinarySolution] = None
        w = [weights[s] for s in problem.objectives_order]
        for solution in solution_list:
            if solution.constraints[0] != 0:
                continue
            v = sum([solution.objectives[i] * w[i] for i in range(problem.objectives_num)])
            if best_value > v:
                best_value = v
                best_solution = solution
        return best_solution
