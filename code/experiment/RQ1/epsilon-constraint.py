# Load the project path
import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)


# from nen.Solver.GASolver import GASolver
# from project_path import PROJECT_PATH
import sys
# sys.path.append(PROJECT_PATH)

from nen import LP, ProblemResult, MethodResult, Problem
from nen.Solver import ExactECSolver


names_NRP = ['rp', 'ms', 'Baan', 'classic-1']
order_NRP = ['cost', 'revenue']
names_FSP = ['BerkeleyDB', 'ERS', 'WebPortal', 'Drupal', 'Amazon', 'E-Shop']
order_FSP = ['COST', 'USED_BEFORE', 'DEFECTS', 'DESELECTED']


for name in names_NRP:
    order = order_NRP
    result_folder = 'EA-GA-{}'.format(name)

    problem = Problem(name)
    problem.vectorize(order)

    # prepare the problem result folder before solving
    problem_result = ProblemResult(name, problem, result_folder)
    lp = LP(name, order)

    # solve with epsilon
    print("start solve {} problem".format(name))
    ea_result = MethodResult('ea', problem_result.path, lp)
    result = ExactECSolver.solve(lp)
    print("end solve {} problem".format(name))
    ea_result.add(result)

    # dump the results
    problem_result.add(ea_result)
    problem_result.dump()

for name in names_FSP:
    order = order_FSP
    result_folder = 'EA-GA-{}'.format(name)

    problem = Problem(name)
    problem.vectorize(order)

    # prepare the problem result folder before solving
    problem_result = ProblemResult(name, problem, result_folder)
    lp = LP(name, order)

    # solve with epsilon
    print("start solve {} problem".format(name))
    ea_result = MethodResult('ea', problem_result.path, lp)
    result = ExactECSolver.solve(lp)
    print("end solve {} problem".format(name))
    ea_result.add(result)

    # dump the results
    problem_result.add(ea_result)
    problem_result.dump()



