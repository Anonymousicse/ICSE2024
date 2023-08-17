from typing import Any, Tuple, List, Dict
import random
from math import exp
from datetime import datetime
from dimod.binary_quadratic_model import BinaryQuadraticModel
from nen.Problem import QP
from nen.Result import Result
from nen.Solver.EmbeddingSampler import EmbeddingSampler
from nen.Term import Quadratic, Constraint
from nen.Solver.MetaSolver import SolverUtil


class SASampler(EmbeddingSampler):
    """ [summary] Simulated Annealing Sampler,
    sample on the QUBO or Hamiltonian but not the original problem.
    """
    @staticmethod
    def random_values(variables: List[Any]) -> Dict[Any, bool]:
        """random_values [summary] randomly generate a values dict.
        """
        return {var: bool(random.randint(0, 1)) for var in variables}

    @staticmethod
    def random_neighbour(values: Dict[Any, bool]) -> Dict[Any, bool]:
        """random_neighbour [summary] flip a var and return itself.
        """
        var = random.choice(list(values.keys()))
        values[var] = not values[var]
        return values

    @staticmethod
    def fitness(values: Dict[Any, bool], H: Quadratic) -> float:
        """fitness [summary] evaluate the fitness with given values and Hamiltonian.
        """
        result = H.constant
        for k, v in H.linear.items():
            if k in values:
                if values[k]: result += v
        for (k1, k2), v in H.quadratic.items():
            if k1 in values and k2 in values:
                if values[k1] and values[k2]: result += v
        return result

    def sample_hamiltonian(self, H: Quadratic, variables: List[str], num_reads: int,
                           t_max: float, t_min: float, alpha: float, exec_time: float,
                           problem: QP, max_stay: int = 150
                           ) -> Tuple[List[Dict[Any, bool]], float]:
        """sample_hamiltonian [summary] sample qubo or hamiltionian without any embedding.
        """
        values_list: List[Dict[Any, bool]] = []
        start = SolverUtil.time()
        # loop num_reads time
        for _ in range(num_reads):
            t = t_max
            s = SASampler.random_values(variables)
            b: Dict[Any, bool] = {}
            # start annealing
            while t > t_min:
                stay_counter = 0
                sn = SASampler.random_neighbour(s)
                d = SASampler.fitness(sn, H) - SASampler.fitness(s, H)
                if (d <= 0) or (random.random() < exp((-d) / t)):
                    s = sn
                if len(b) == 0 or SASampler.fitness(s, H) < SASampler.fitness(b, H):
                    b = s
                    stay_counter = 0
                else:
                    stay_counter += 1
                if stay_counter > max_stay:
                    break
                t *= alpha
            values_list.append(b)
            if (SolverUtil.time() - start) > exec_time:
                break
        elapsed = SolverUtil.time() - start
        return values_list, elapsed

    @staticmethod
    def bolshevik(chain: List[bool]) -> bool:
        """bolshevik [summary] return majority value in a chain,
           random return one if neither of T/F domins.
        """
        T, F = 0, 0
        for v in chain:
            if v:
                T += 1
            else:
                F += 1
        if T == F:
            return bool(random.randint(0, 1))
        elif T > F:
            return True
        else:
            return False

    def embed_sample(self, H: Quadratic, variables: List[str], num_reads: int,
                     t_max: float, t_min: float, alpha: float, exec_time: float,
                     problem: QP
                     ) -> Tuple[List[Dict[str, bool]], float]:
        """embed_sample [summary] embed in a Quantum Annealing way and then sample.
        """
        # convert quadratic to qubo to bqm
        qubo = Constraint.quadratic_to_qubo_dict(H)
        bqm = BinaryQuadraticModel.from_qubo(qubo)
        # embed, embedding: var -> (qi), bqm_embedded: q -> bias, (q, q) -> offset
        embedding, bqm_embedded = self.embed(bqm)
        # get Hamiltion(Quadratic) from embedded bqm (for evaluation)
        # NOTE: For dicts in bqm_embededd, their keys are int(qubit index) but not the str(var)
        embedded_H = Quadratic(quadratic=bqm_embedded.quadratic, linear=bqm_embedded.linear)
        # get embedded variables
        embedded_variables = set()
        for k in embedded_H.linear:
            embedded_variables.add(k)
        for (k1, k2) in embedded_H.quadratic:
            embedded_variables.add(k1)
            embedded_variables.add(k2)

        # sample
        embeded_values_list, elapsed = \
            self.sample_hamiltonian(embedded_H, list(embedded_variables), num_reads, t_max, t_min,
                                    alpha, exec_time, problem)

        # unembed values
        values_list: List[Dict[str, bool]] = []
        for embeded_values in embeded_values_list:
            values: Dict[str, bool] = {}
            for var in variables:
                chain = [embeded_values[qubit] for qubit in embedding[var]]
                values[var] = SASampler.bolshevik(chain)
            values_list.append(values)

        # return
        return values_list, elapsed

    def sa_sample(self, H: Quadratic, variables: List[str],
                  if_embed: bool, num_reads: int,
                  t_max: float, t_min: float, alpha: float, exec_time: float,
                  problem: QP
                  ) -> Tuple[List[Dict[str, bool]], float]:
        random.seed(datetime.now())
        if if_embed:
            return self.embed_sample(H, variables, num_reads, t_max, t_min, alpha, exec_time, problem)
        else:
            return self.sample_hamiltonian(H, variables, num_reads, t_max, t_min, alpha, exec_time, problem)


class SAQPSolver:
    """ [summary] Simulated Annealing Quadratic Programming Solver.
    """
    @staticmethod
    def solve(problem: QP, weights: Dict[str, float], if_embed: bool,
              num_reads: int, t_max: float, t_min: float, alpha: float, exec_time: float = 1e6) -> Result:
        # check arguments
        assert t_min < t_max
        assert 0 <= alpha <= 1
        print("start SA to solve {}".format(problem.name))
        # modelling
        wso = Quadratic(linear=SolverUtil.weighted_sum_objective(problem.offset_objectives, weights))
        penalty = EmbeddingSampler.calculate_penalty(wso, problem.constraint_sum)
        H = Constraint.quadratic_weighted_add(1, penalty * 1000, wso, problem.constraint_sum)
        # sample
        sampler = SASampler()
        values_list, elapsed = \
            sampler.sa_sample(H, problem.variables, if_embed, num_reads, t_max, t_min, alpha, exec_time, problem)
        # add into result
        result = Result(problem)
        solution_list = []
        for values in values_list:
            solution = problem.evaluate(values)
            solution_list.append(solution)
        # w = []
        # for k, v in weights.items():
        #     w.append(v)
        # solution_list.sort(key=lambda x: (x.constraints[0], sum([x.objectives[i] * w[i] for i in range(problem.objectives_num)])))
        # solution_list = solution_list[:num_reads]
        for solution in solution_list:
            result.wso_add(solution)
        result.elapsed = elapsed
        print("end SA to solve")
        return result
