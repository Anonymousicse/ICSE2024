from typing import Dict, List

import hybrid
from dimod import BinaryQuadraticModel
from dwave.system import LeapHybridSampler
# from dwave.system import DWaveSampler

from nen.Solver import MOQASolver, SOQA
from nen.Term import Constraint, Quadratic
from nen.Problem import QP
from nen.Result import Result
from nen.Solver.MetaSolver import SolverUtil
from nen.Solver.EmbeddingSampler import EmbeddingSampler, SampleSet


class DwaveHybridSolver:
    """ [summary] HybridSolver, stands for Multi-Objective Quantum Annealling with HybridSolver,
    hybrid—quantum-classical hybrid; typically one or more classical algorithms run on the problem
    while outsourcing to a quantum processing unit (QPU) parts of the problem where it benefits most.

    The Quantum Annealling Solver is implemeneted with D-Wave Leap,
    make sure the environment is configured successfully accordingly.
    """

    @staticmethod
    def solve(problem: QP, sample_times: int, num_reads: int, num_sweeps: int = 1000) -> Result:
        """solve [summary] solve multi-objective qp, results are recorded in result.
        """
        print("start Hybrid Solver to solve multi-objective problem!!!")
        # scale objectives and get the basic
        basic_weights = SolverUtil.scaled_weights(problem.objectives)
        # sample for sample_times times
        samplesets: List[SampleSet] = []
        elapseds: List[float] = []
        for _ in range(sample_times):
            for _ in range(num_reads):
                # generate random weights and calculate weighted sum obejctive
                weights = MOQASolver.random_normalized_weights(basic_weights)
                wso = Quadratic(linear=SolverUtil.weighted_sum_objective(problem.objectives, weights))
                # calculate the penalty and add constraints to objective with penalty
                penalty = EmbeddingSampler.calculate_penalty(wso, problem.constraint_sum)
                objective = Constraint.quadratic_weighted_add(1, penalty, wso, problem.constraint_sum)
                qubo = Constraint.quadratic_to_qubo_dict(objective)
                # convert qubo to bqm
                bqm = BinaryQuadraticModel.from_qubo(qubo)

                # define the workflow
                workflow = hybrid.Loop(
                    hybrid.Race(
                        hybrid.SimulatedAnnealingProblemSampler(num_reads=1, num_sweeps=num_sweeps),
                        hybrid.EnergyImpactDecomposer(size=50, rolling=True, traversal='pfs')
                        | hybrid.QPUSubproblemAutoEmbeddingSampler(num_reads=1)
                        | hybrid.SplatComposer()) | hybrid.ArgMin(), convergence=3, max_iter=1000)
                # Solve in Hybrid-QA
                sampler = hybrid.HybridSampler(workflow)
                start = SolverUtil.time()
                sampleset = sampler.sample(bqm)
                end = SolverUtil.time()
                # while len(sampleset.record) == 0:
                #     sampleset = sampler.sample(bqm)
                if sampleset.info.get('timing'):
                    elapsed = sampleset.info['timing']['qpu_sampling_time'] / 1000_000
                else:
                    elapsed = end - start

                samplesets.append(sampleset)
                elapseds.append(elapsed)
        # put samples into result
        result = Result(problem)
        for sampleset in samplesets:
            for values in EmbeddingSampler.get_values(sampleset, problem.variables):
                solution = problem.evaluate(values)
                result.add(solution)
        # add into method result
        result.elapsed = sum(elapseds)
        for sampleset in samplesets:
            if 'solving info' not in result.info:
                result.info['solving info'] = [sampleset.info]
            else:
                result.info['solving info'].append(sampleset.info)
        # storage parameters
        result.info['sample_times'] = sample_times
        result.info['num_reads'] = num_reads
        result.iterations = sample_times
        print("Hybrid Solver end!!!")
        return result

    @staticmethod
    def single_solve(problem: QP, weights: Dict[str, float], num_reads: int,
                     sample_times: int, step_count: int = 1, num_sweeps: int = 1000) -> Result:
        print("start Hybrid Solver to solve single-problem!!!")
        result = Result(problem)
        # prepare wso objective
        wso = Quadratic(linear=SolverUtil.weighted_sum_objective(problem.objectives, weights))
        penalty = EmbeddingSampler.calculate_penalty(wso, problem.constraint_sum)
        # add constraints to objective with penalty
        objective = Constraint.quadratic_weighted_add(1, penalty, wso, problem.constraint_sum)
        qubo = Constraint.quadratic_to_qubo_dict(objective)
        # convert qubo to bqm
        bqm = BinaryQuadraticModel.from_qubo(qubo)

        assert num_reads % step_count == 0
        num_ = int(num_reads / step_count)

        # define the workflow
        workflow = hybrid.Loop(
            hybrid.Race(
                hybrid.SimulatedAnnealingProblemSampler(num_reads=num_, num_sweeps=num_sweeps),
                hybrid.EnergyImpactDecomposer(size=50, rolling=True, traversal='pfs')
                | hybrid.QPUSubproblemAutoEmbeddingSampler(num_reads=num_)
                | hybrid.SplatComposer()) | hybrid.ArgMin(), convergence=3, max_iter=1000)

        for _ in range(sample_times):
            res = DwaveHybridSolver.solve_once(problem=problem, weights=weights, bqm=bqm, sample_times=step_count,
                                          num_reads=num_, workflow=workflow)
            result.solution_list.append(res.single)
            result.elapsed += res.elapsed
        result.info['weights'] = weights
        result.info['penalty'] = penalty
        result.info['num_reads'] = num_reads
        result.iterations = sample_times
        print("Hybrid Solver end!!!")
        return result

    @staticmethod
    def solve_once(problem: QP, weights: Dict[str, float], num_reads: int,
                   sample_times: int, bqm, workflow) -> Result:
        """solve [summary] solve single objective qp (applied wso technique), return Result.
        the result return from hybrid.HybridSampler is an object of 'concurrent.futures.Future',
        not an object of 'dimod.SampleSet', so we need to convert the result to  'dimod.SampleSet' by 'from_future'
        """
        result = Result(problem)
        samplesets = []
        # Solve in QA
        sampler = hybrid.HybridSampler(workflow)
        for _ in range(sample_times):
            start = SolverUtil.time()
            sampleset = sampler.sample(bqm)
            # while len(sampleset.record) == 0:
            #     sampleset = sampler.sample(bqm)
            end = SolverUtil.time()
            if sampleset.info.get('timing'):
                elapsed = sampleset.info['timing']['qpu_sampling_time'] / 1000_000
            else:
                elapsed = end - start
            result.elapsed += elapsed
            samplesets.append(sampleset)
        # get results
        solution_list = []
        iteration = 0
        assert len(samplesets) == sample_times
        for sampleset in samplesets:
            iteration += 1
            # print(iteration, '++++++++++')
            for values, occurrence in EmbeddingSampler.get_values_and_occurrence(sampleset, problem.variables):
                solution = problem.evaluate(values)
                solution_list.append(solution)
        best_solution = SOQA.best_solution(solution_list=solution_list, weights=weights, problem=problem)
        result.wso_add(best_solution)
        result.info['sample_times'] = sample_times
        result.info['num_reads'] = num_reads
        result.iterations = sample_times
        return result
