from typing import Dict
from tabu import TabuSampler
from dimod.binary_quadratic_model import BinaryQuadraticModel
from nen.Term import Quadratic, Constraint
from nen.Solver.MetaSolver import SolverUtil
from nen.Solver.EmbeddingSampler import EmbeddingSampler
from nen.Problem import QP
from nen.Result import Result


class TabuQPSolver:
    """ [summary] Tabu Search Quadratic Programming Solver.
    """
    @staticmethod
    def solve(problem: QP, weights: Dict[str, float], num_reads: int) -> Result:
        # modelling
        wso = Quadratic(linear=SolverUtil.weighted_sum_objective(problem.objectives, weights))
        penalty = EmbeddingSampler.calculate_penalty(wso, problem.constraint_sum)
        objective = Constraint.quadratic_weighted_add(1, penalty, wso, problem.constraint_sum)
        qubo = Constraint.quadratic_to_qubo_dict(objective)
        bqm = BinaryQuadraticModel.from_qubo(qubo)
        # solve with Tabu
        sampler = TabuSampler()
        start = SolverUtil.time()
        sampleset = sampler.sample(bqm, num_reads=num_reads)
        elapsed = SolverUtil.time() - start
        # add to Result
        result = Result(problem)
        for values in EmbeddingSampler.get_values(sampleset, problem.variables):
            solution = problem.evaluate(values)
            result.add(solution)
        result.elapsed = elapsed
        return result
