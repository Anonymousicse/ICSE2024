from typing import Dict, List, Any

from jmetal.core.solution import BinarySolution

from nen.Term import Constraint, Quadratic
from nen.Problem import QP
from nen.Result import Result, NDArchive
from nen.Solver.MetaSolver import SolverUtil
from nen.Solver.EmbeddingSampler import EmbeddingSampler


class RQAWSOSolver:
    """ [summary]R QAWSOSolver, stands for Refinement-based Quantum Annealling Weighted Sum Objective Solver.

    The Quantum Annealling Solver is implemeneted with D-Wave Leap,
    make sure the environment is configured successfully accordingly.
    """
    @staticmethod
    def solve(problem: QP,
              weights: Dict[str, float],
              penalty: float,
              max_reverse_loop: int,
              anneal_schedule: List[List[Any]],
              num_reads: int,
              is_single: bool = False) -> Result:
        """solve [summary] solve single objective qp (applied wso technique), result in result.
        """
        # prepare wso objective
        wso = SolverUtil.weighted_sum_objective(problem.objectives, weights)
        # add constraints to objective with penalty
        objective = Constraint.quadratic_weighted_add(1, penalty, Quadratic(linear=wso), problem.constraint_sum)
        qubo = Constraint.quadratic_to_qubo_dict(objective)
        # Solve in QA
        sampler = EmbeddingSampler()
        print("enter D-Wave to finish reverse quantum annealing")
        samplesets = \
            sampler.refinement_sample(qubo=qubo, max_reverse_loop=max_reverse_loop,
                                      anneal_schedule=anneal_schedule,
                                      select=EmbeddingSampler.select_by_energy,
                                      dominate=EmbeddingSampler.engery_compare,
                                      num_reads=num_reads)
        print("finish reverse quantum annealing")
        # use the last sampleset
        # beacause in the samplesets, the later data is better
        sampleset = samplesets[-1]
        elapsed = sum([EmbeddingSampler.get_qpu_time(sampleset) for sampleset in samplesets])
        # get results
        result = Result(problem)
        if 'occurence' not in result.info:
            result.info['occurence'] = {}
        for values, occurrence in EmbeddingSampler.get_values_and_occurrence(sampleset, problem.variables):
            # solution record the num of objective
            solution: BinarySolution
            if is_single:
                solution = problem.wso_evaluate(values, weights)
            else:
                solution = problem.evaluate(values)
            result.wso_add(solution)
            key = NDArchive.bool_list_to_str(solution.variables[0])
            if key not in result.info['occurence']:
                result.info['occurence'][key] = str(occurrence)
            else:
                result.info['occurence'][key] = str(int(result.info['occurence'][key]) + occurrence)
        result.elapsed = elapsed
        if 'solving info' not in result.info:
            result.info['solving info'] = [sampleset.info]
        else:
            result.info['solving info'].append(sampleset.info)
        # storage parameters
        result.info['weights'] = weights
        result.info['penalty'] = penalty
        result.info['num_reads'] = num_reads
        return result
