import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from nen import Problem, ProblemResult, MethodResult, QP
from nen.Solver.HybridSolver import HybridSolver

names_NRP = ['classic-3']
order_NRP = ['cost', 'revenue']
weight_NRP = {'cost': 1 / 2, 'revenue': 1 / 2}

names_FSP = ['uClinux']
order_FSP = ['COST', 'USED_BEFORE', 'DEFECTS', 'DESELECTED']
weight_FSP = {'COST': 1 / 4, 'USED_BEFORE': 1 / 4, 'DEFECTS': 1 / 4, 'DESELECTED': 1 / 4}

rates = [0.3, 0.5, 0.7, 0.8, 0.9]

hymoo_result_folder = 'hy_scale'

for name in names_NRP:
    for rate in rates:
        order = order_NRP
    
        problem = QP(name, order)
        problem.vectorize(order)

        # prepare the problem result folder before solving
        problem_result = ProblemResult(name, problem, hymoo_result_folder)

        # solve with cplex
        hy_result = MethodResult('hybrid{}'.format(rate), problem_result.path, problem)
        for _ in range(1):
            result = HybridSolver.solve(problem=problem, sample_times=10, num_reads=500,
                                        sub_size=150, rate=rate, annealing_time=20)
            hy_result.add(result)

        # dump the results
        problem_result.add(hy_result)
        problem_result.dump()


for name in names_FSP:
    for rate in rates:
        order = order_FSP

        problem = QP(name, order)
        problem.vectorize(order)

        # prepare the problem result folder before solving
        problem_result = ProblemResult(name, problem, hymoo_result_folder)

        # solve with cplex
        hy_result = MethodResult('hybrid{}'.format(rate), problem_result.path, problem)
        for _ in range(1):
            result = HybridSolver.solve(problem=problem, sample_times=10, num_reads=500,
                                        sub_size=150, rate=rate, annealing_time=20)
            hy_result.add(result)

        # dump the results
        problem_result.add(hy_result)
        problem_result.dump()
