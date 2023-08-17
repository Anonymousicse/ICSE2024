# Put this file at Nen/ (Project Root Path)
from nen import Problem
from nen.Solver import JarSolver

from nen import ProblemResult, MethodResult

# names_FSP = ['E-Shop', 'eCos', 'uClinux', 'Amazon'] # maxEvaluations=20000
# names_FSP = ['eCos', 'uClinux'] # maxEvaluations=60000
names_FSP = ['axTLS', 'toybox', 'uClinux', 'SPLOT-Generated', 'SPLOT-Generated-2']
order_FSP = ['COST', 'USED_BEFORE', 'DEFECTS', 'DESELECTED']
weight_FSP = {'COST': 1 / 4, 'USED_BEFORE': 1 / 4, 'DEFECTS': 1 / 4, 'DESELECTED': 1 / 4}

# names_NRP = ['classic-1', 'classic-2', 'classic-3', 'Baan'] # maxEvaluations=10000
names_NRP = ['classic-2', 'classic-3', 'classic-5', 'classic-4']
order_NRP = ['cost', 'revenue']
weight_NRP = {'cost': 1 / 2, 'revenue': 1 / 2}

result_folder = 'nsgaii_5_500_500000_500000'

for name in names_NRP:
    problem = Problem(name)
    problem.vectorize(order_NRP)

    # prepare the problem result folder before solving
    problem_result = ProblemResult(name, problem, result_folder)

    # solve with NSGA-II
    JarSolver.solve(
        solver_name='NSGAII', config_name='tmp_config',
        problem=name, objectiveOrder=order_NRP, iterations=5,
        populationSize=500, maxEvaluations=500000,
        crossoverProbability=0.8, mutationProbability=(1 / problem.variables_num),
        resultFolder=result_folder, methodName='nsgaii', exec_time=-1
    )
    # load results
    ea_result = MethodResult('nsgaii', problem_result.path, problem)
    ea_result.load(evaluate=True, single_flag=True)
    ea_result.make_method_result(single_flag=True)
    problem_result.add(ea_result)
    problem_result.dump()

for name in names_FSP:
    problem = Problem(name)
    problem.vectorize(order_FSP)

    # prepare the problem result folder before solving
    problem_result = ProblemResult(name, problem, result_folder)

    # solve with NSGA-II
    JarSolver.solve(
        solver_name='NSGAII', config_name='tmp_config',
        problem=name, objectiveOrder=order_FSP, iterations=5,
        populationSize=500, maxEvaluations=500000,
        crossoverProbability=0.8, mutationProbability=(1 / problem.variables_num),
        resultFolder=result_folder, methodName='nsgaii', exec_time=-1
    )

    # load results
    ea_result = MethodResult('nsgaii', problem_result.path, problem)
    ea_result.load(evaluate=True, single_flag=True)
    ea_result.make_method_result(single_flag=True)
    problem_result.add(ea_result)
    problem_result.dump()
