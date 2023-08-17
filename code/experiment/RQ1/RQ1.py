import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from nen import Problem, ProblemResult, MethodResult, Visualizer

# names_FSP = ['ERS', 'WebPortal', 'Drupal']
names_FSP = ['ERS', 'WebPortal', 'Drupal']
order_FSP = ['COST', 'USED_BEFORE', 'DEFECTS', 'DESELECTED']
weight_FSP = {'COST': 1 / 4, 'USED_BEFORE': 1 / 4, 'DEFECTS': 1 / 4, 'DESELECTED': 1 / 4}

names_NRP = ['rp', 'ms', 'Baan', 'classic-1']
order_NRP = ['cost', 'revenue']
weight_NRP = {'cost': 1 / 2, 'revenue': 1 / 2}

nsgaii_result_folder = 'nsgaii_5_100_20000_20000'
moqa_result_folder = 'moqa_10_500_20'
exact_result_folder = 'ea'

# compare MOQA with NSGA-II
for name in names_FSP:
    problem = Problem(name)
    problem.vectorize(order_FSP)

    # prepare the problem result folder before solving
    exact_problem_result = ProblemResult(name, problem, exact_result_folder)
    nsgaii_problem_result = ProblemResult(name, problem, nsgaii_result_folder)
    moqa_problem_result = ProblemResult(name, problem, moqa_result_folder)

    ga_result = MethodResult('nsgaii', nsgaii_problem_result.path, problem)
    ga_result.load()
    qa_result = MethodResult('moqa', moqa_problem_result.path, problem)
    qa_result.load()
    ea_result = MethodResult('ea', exact_problem_result.path, problem)
    ea_result.load()

    moqa_problem_result.add(ga_result)
    moqa_problem_result.add(qa_result)
    moqa_problem_result.add(ea_result)

    # compare
    scores_ga = moqa_problem_result.average_list_compare(methods=['nsgaii', 'moqa', 'ea'])
    table_ga = Visualizer.tabulate_single_problem(
        name, ['moqa', 'nsgaii', 'ea'], ['elapsed time', 'found', 'front', 'igd', 'hv', 'spacing', 'tts'],
        scores_ga, {'elapsed time': 4, 'found': 5, 'front': 4, 'igd': 4, 'hv': 4, 'spacing': 4, 'tts': 4}
    )
    Visualizer.tabluate(table_ga, 'moqa-nsgaii-ga-compare-{}.csv'.format(name))


for name in names_NRP:
    problem = Problem(name)
    problem.vectorize(order_NRP)

    # prepare the problem result folder before solving
    exact_problem_result = ProblemResult(name, problem, exact_result_folder)
    nsgaii_problem_result = ProblemResult(name, problem, nsgaii_result_folder)
    moqa_problem_result = ProblemResult(name, problem, moqa_result_folder)

    ga_result = MethodResult('nsgaii', nsgaii_problem_result.path, problem)
    ga_result.load()
    qa_result = MethodResult('moqa', moqa_problem_result.path, problem)
    qa_result.load()
    ea_result = MethodResult('ea', exact_problem_result.path, problem)
    ea_result.load()

    moqa_problem_result.add(ga_result)
    moqa_problem_result.add(qa_result)
    moqa_problem_result.add(ea_result)

    # compare
    scores_ga = moqa_problem_result.average_list_compare(methods=['nsgaii', 'moqa', 'ea'])
    table_ga = Visualizer.tabulate_single_problem(
        name, ['moqa', 'nsgaii', 'ea'], ['elapsed time', 'found', 'front', 'igd', 'hv', 'spacing', 'tts'],
        scores_ga, {'elapsed time': 4, 'found': 5, 'front': 4, 'igd': 4, 'hv': 4, 'spacing': 4, 'tts': 4}
    )
    Visualizer.tabluate(table_ga, 'moqa-nsgaii-ga-compare-{}.csv'.format(name))