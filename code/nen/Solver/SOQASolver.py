from typing import Dict, List, Union

import numpy as np
from jmetal.core.solution import BinarySolution
from nen.Term import Constraint, Quadratic
from nen.Problem import QP
from nen.Result import Result, NDArchive
from nen.Solver.MetaSolver import SolverUtil
from nen.Solver.EmbeddingSampler import EmbeddingSampler


class SOQASolver:
    """ [summary] SOQA, stands for Quantum Annealling Weighted Sum Objective Solver as Single Objective Problem.

    The Quantum Annealling Solver is implemeneted with D-Wave Leap,
    make sure the environment is configured successfully accordingly.
    """

    @staticmethod
    def solve(problem: QP, weights: Dict[str, float], num_reads: int, step_count: int = 1, sample_times: int = 1) -> Result:
        """
        Parameters
        -------------
        problem: QP
            the problem to be solved
        weights: Dict[str, float]
            weights to convert a multi-objective problem into a single-objective problem
        num_reads: int
            total solution numbers per execution
        step_count: int
            The number of times the algorithm calls the sampler loop sampling per execution
        sample_times: int
            loop execution SOQA times
        """
        print("{} start SOQA to solve single-problem!!!".format(problem.name))
        result = Result(problem)
        wso = Quadratic(linear=SolverUtil.weighted_sum_objective(problem.objectives, weights))
        # calculate the penalty and add constraints to objective with penalty
        penalty = EmbeddingSampler.calculate_penalty(wso, problem.constraint_sum)
        assert num_reads % step_count == 0
        num_ = int(num_reads / step_count)
        for _ in range(sample_times):
            res = SOQASolver.solve_once(problem=problem, weights=weights, penalty=penalty, sample_times=step_count,
                                        num_reads=num_)
            result.solution_list.append(res.single)
            result.elapsed += res.elapsed
            if 'occurence' not in result.info:
                result.info['occurence'] = {}
            else:
                result.info['occurence'] = res.info['occurence']
            if 'solving info' not in result.info:
                result.info['solving info'] = res.info['solving info']
            else:
                result.info['solving info'].append(res.info['solving info'])
        result.info['weights'] = weights
        result.info['penalty'] = penalty
        result.info['num_reads'] = num_reads
        result.iterations = sample_times
        print("{} SOQA end!!!".format(problem.name))
        return result

    @staticmethod
    def solve_once(problem: QP, weights: Dict[str, float], penalty: float, num_reads: int, sample_times: int) -> Result:
        """solve [summary] solve single objective qp (applied wso technique), return Result.
        """
        # prepare wso objective
        wso = SolverUtil.weighted_sum_objective(problem.objectives, weights)
        # add constraints to objective with penalty
        objective = Constraint.quadratic_weighted_add(1, penalty, Quadratic(linear=wso), problem.constraint_sum)
        qubo = Constraint.quadratic_to_qubo_dict(objective)
        # Solve in QA
        result = Result(problem)
        samplesets = []
        sampler = EmbeddingSampler()
        for _ in range(sample_times):
            sampleset, elapsed = sampler.sample(qubo, num_reads=num_reads)
            result.elapsed += elapsed
            samplesets.append(sampleset)
        # get results
        solution_list = []
        for sampleset in samplesets:
            if 'solving info' not in result.info:
                result.info['solving info'] = [sampleset.info]
            else:
                result.info['solving info'].append(sampleset.info)
            if 'occurence' not in result.info:
                result.info['occurence'] = {}
            for values, occurrence in EmbeddingSampler.get_values_and_occurrence(sampleset, problem.variables):
                solution = problem.evaluate(values)
                solution_list.append(solution)

                key = NDArchive.bool_list_to_str(solution.variables[0])
                if key not in result.info['occurence']:
                    result.info['occurence'][key] = str(occurrence)
                else:
                    result.info['occurence'][key] = str(int(result.info['occurence'][key]) + occurrence)
        solution_list.sort(key=lambda x: np.dot(x.objectives, list(weights.values())))
        best_solution = SOQASolver.best_solution(solution_list=solution_list, weights=weights, problem=problem, violated_count=False)
        result.wso_add(best_solution)
        return result

    @staticmethod
    def best_solution(solution_list: List[BinarySolution], problem: QP,
                      weights: Dict[str, float], violated_count: bool = True) -> Union[None, BinarySolution]:
        """best_solution [summary] get the best solution from the archive with certain weights.
        """
        best_value_all: float = float('inf')
        best_solution_all: Union[None, BinarySolution] = None
        best_value: float = float('inf')
        best_solution: Union[None, BinarySolution] = None
        w = [weights[s] for s in problem.objectives_order]
        for solution in solution_list:
            v = sum([solution.objectives[i] * w[i] for i in range(problem.objectives_num)])
            if best_value_all > v:
                best_value_all = v
                best_solution_all = solution
            if violated_count:
                if best_value > v and sum(solution.constraints) == 0:
                    best_value = v
                    best_solution = solution
        if best_solution is None:
            best_solution = best_solution_all
        return best_solution
