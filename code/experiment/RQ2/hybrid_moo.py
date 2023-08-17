# Put this file at Nen/ (Project Root Path)
import sys
import os


curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from nen import Problem, ProblemResult, MethodResult, QP
from nen.Solver.HybridSolver import HybridSolver


names_FSP = ['axTLS', 'toybox', 'uClinux', 'SPLOT-Generated', 'SPLOT-Generated-3']
order_FSP = ['COST', 'USED_BEFORE', 'DEFECTS', 'DESELECTED']
weight_FSP = {'COST': 1 / 4, 'USED_BEFORE': 1 / 4, 'DEFECTS': 1 / 4, 'DESELECTED': 1 / 4}

names_NRP = ['classic-2', 'classic-4', 'classic-3', 'classic-5']
# names_NRP = ['classic-5', 'classic-4']
order_NRP = ['cost', 'revenue']
weight_NRP = {'cost': 1 / 2, 'revenue': 1 / 2}

result_folder = 'hybrid_10_500_150_2'

for name in names_NRP:
    problem = Problem(name)
    problem.vectorize(order_NRP)

    # prepare the problem result folder before solving
    problem_result = ProblemResult(name, problem, result_folder)
    qp = QP(name, order_NRP)
    hy_result = MethodResult('hybrid', problem_result.path, qp)

    # solve with Genetic Algorithm
    for _ in range(1):
        result = HybridSolver.solve(problem=qp, sample_times=10, num_reads=500, 
                                    sub_size=150, steps=1, annealing_time=20)
        hy_result.add(result)

    # dump the results
    problem_result.add(hy_result)
    problem_result.dump()

for name in names_FSP:
    problem = Problem(name)
    problem.vectorize(order_FSP)

    # prepare the problem result folder before solving
    problem_result = ProblemResult(name, problem, result_folder)
    qp = QP(name, order_FSP)
    hy_result = MethodResult('hybrid', problem_result.path, qp)

    # solve with Genetic Algorithm
    for _ in range(1):
        result = HybridSolver.solve(problem=qp, sample_times=1, num_reads=500, 
                                    sub_size=150, steps=1, annealing_time=100)
        hy_result.add(result)

    # dump the results
    problem_result.add(hy_result)
    problem_result.dump()