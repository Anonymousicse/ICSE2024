from typing import Any, Tuple, List, Dict
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.pntx import TwoPointCrossover, SinglePointCrossover
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.operators.sampling.rnd import BinaryRandomSampling
from pymoo.optimize import minimize
from pymoo.termination.default import DefaultMultiObjectiveTermination, DefaultSingleObjectiveTermination
from pymoo.algorithms.base.genetic import GeneticAlgorithm
from pymoo.algorithms.soo.nonconvex.ga import GA
from nen.Problem import PymooProblem, QP, PysooProblem
from nen.Problem import Problem
from nen.Result import Result


class GASolver:
    """ [summary] GASolver, stands for Multi-Objective Genetic Algorithm Solver,
        it adopts random weighted sum of objectives and use Genetic Algorithm to solve problem for several times.

        The Genetic Algorithm Solver is implemented with 'pymoo' python package,
        make sure the environment is configured successfully accordingly.
        """
    @staticmethod
    def solve(problem: Problem, populationSize: int, maxEvaluations: int, seed: int,
              crossoverProbability: float, mutationProbability: int, verbose: bool = False, 
              iterations: int = 1, exec_time: float = 1e6, single_flag: bool = False, 
              weights: Dict[str, float] = None) -> Result:
        """
        seed : integer
            The random seed to be used.
        verbose : bool
            Whether output should be printed or not.
        populationSize : integer
            Equivalent to 'num_reads' in QA
        Returns
        --------
        res.X: Design space values are
        res.F: Objective spaces values
        res.G: Constraint values
        res.CV: Aggregated constraint violation
        res.algorithm: Algorithm object which has been iterated over
        res.opt: The solutions as a Population-Pareto object.
                If the least feasible solution should be returned when no feasible solution was found,
                the flag return_least_infeasible can be enabled
        res.pop: The final Population. The values from the final population can be extracted by using the 'get' method.
                example: res.pop.get('X')
        res.history: The history of the algorithm. (only if save_history has been enabled during the algorithm initialization)
        res.time: The time required to run the algorithm
        """
        
        result = Result(problem)
        termination = DefaultMultiObjectiveTermination(
            n_max_evals=maxEvaluations
        )
        termination_single = DefaultSingleObjectiveTermination(
            n_max_evals=maxEvaluations
        )
        pro = PymooProblem(problem)
        alg = NSGA2(pop_size=populationSize,
                    # n_offsprings=10,
                    sampling=BinaryRandomSampling(),
                    # crossover=SBX(prob=crossoverProbability, eta=15),
                    crossover=SinglePointCrossover(prob=crossoverProbability),
                    # mutation=PolynomialMutation(eta=20, prob=mutationProbability),
                    mutation=BitflipMutation(prob=mutationProbability),
                    # eliminate_duplicates=True
                    )
        if single_flag:
            pro_single = PysooProblem(problem=problem, weights=weights)
            alg_single = GA(
                        pop_size=populationSize,
                        # n_offsprings=10,
                        sampling=BinaryRandomSampling(),
                        # crossover=SBX(prob=crossoverProbability, eta=15),
                        crossover=SinglePointCrossover(prob=crossoverProbability),
                        # mutation=PolynomialMutation(eta=20, prob=mutationProbability),
                        mutation=BitflipMutation(prob=mutationProbability),
                        # eliminate_duplicates=False
                        )

        for _ in range(iterations):
            if single_flag:
                print("{} start Genetic Algorithm to solve single objective problem!!!".format(problem.name))
                res = minimize(pro_single, alg_single, termination_single, seed=seed, verbose=verbose, return_least_infeasible=True)
            else: 
                print("{} start Genetic Algorithm to solve multi-objective problem!!!".format(problem.name))
                res = minimize(pro, alg, termination, seed=seed, verbose=verbose, return_least_infeasible=True)
            # return_least_infeasible=True

            result.elapsed += res.exec_time
            for sol in res.pop:
                val = list(sol.X.flatten())
                values = problem.convert_to_BinarySolution(val)
                solution = problem.evaluate(values)
                result.wso_add(solution)
            if result.elapsed > exec_time:
                break
        result.iterations = iterations
        result.total_num_anneals = populationSize * iterations
        print("Genetic Algorithm end!!!")
        return result

