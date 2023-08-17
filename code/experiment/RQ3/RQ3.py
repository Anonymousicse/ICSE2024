import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from nen import Problem, ProblemResult, MethodResult, Visualizer

names_FSP = ['uClinux']
order_FSP = ['COST', 'USED_BEFORE', 'DEFECTS', 'DESELECTED']
weight_FSP = {'COST': 1 / 4, 'USED_BEFORE': 1 / 4, 'DEFECTS': 1 / 4, 'DESELECTED': 1 / 4}

names_NRP = ['classic-3']
order_NRP = ['cost', 'revenue']
weight_NRP = {'cost': 1 / 2, 'revenue': 1 / 2}

rates = [0.3, 0.5, 0.7, 0.9]

hy_scale_result_folder = 'hy_scale'
hymoo_result_folder = 'hybrid_10_500_150_1'

# compare CQHA with NSGA-II
for name in names_NRP:
    problem = Problem(name)
    problem.vectorize(order_NRP)

    # prepare the problem result folder before solving
    hy_problem_result = ProblemResult(name, problem, hymoo_result_folder)
    hy_scale_problem_result = ProblemResult(name, problem, hy_scale_result_folder)

    hy_result = MethodResult('hybrid', hy_problem_result.path, problem)
    hy_result.load()
    hy_problem_result.add(hy_result)

    methods = []
    for rate in rates:
        methods.append('hybrid{}'.format(rate))
    for method in methods:
        hy_result = MethodResult(method, hy_scale_problem_result.path, problem)
        hy_result.load()
        hy_problem_result.add(hy_result)
    methods.append('hybrid')

    # compare
    scores_hy = hy_problem_result.average_list_compare(methods=methods)
    table_hy = Visualizer.tabulate_single_problem(
        name, [method for method in methods], ['elapsed time', 'found', 'front', 'igd', 'hv', 'spacing', 'tts'],
        scores_hy, {'elapsed time': 2, 'found': 2, 'front': 2, 'igd': 2, 'hv': 2, 'spacing': 2, 'tts': 2}
    )
    Visualizer.tabluate(table_hy, 'hybrid-scale-compare-{}.csv'.format(name))

for name in names_FSP:
    problem = Problem(name)
    problem.vectorize(order_FSP)

    # prepare the problem result folder before solving
    hy_problem_result = ProblemResult(name, problem, hymoo_result_folder)
    hy_scale_problem_result = ProblemResult(name, problem, hy_scale_result_folder)

    hy_result = MethodResult('hybrid', hy_problem_result.path, problem)
    hy_result.load()
    hy_problem_result.add(hy_result)

    methods = []
    for rate in rates:
        methods.append('hybrid{}'.format(rate))
    for method in methods:
        hy_result = MethodResult(method, hy_scale_problem_result.path, problem)
        hy_result.load()
        hy_problem_result.add(hy_result)
    methods.append('hybrid')

    # compare
    scores_hy = hy_problem_result.average_list_compare(methods=methods)
    table_hy = Visualizer.tabulate_single_problem(
        name, [method for method in methods], ['elapsed time', 'found', 'front', 'igd', 'hv', 'spacing', 'tts'],
        scores_hy, {'elapsed time': 2, 'found': 2, 'front': 2, 'igd': 2, 'hv': 2, 'spacing': 2, 'tts': 2}
    )
    Visualizer.tabluate(table_hy, 'hybrid-scale-compare-{}.csv'.format(name))
