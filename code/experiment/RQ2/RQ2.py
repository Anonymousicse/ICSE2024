import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from nen import Problem, ProblemResult, MethodResult, Visualizer

names_FSP = ['eCos', 'uClinux']
order_FSP = ['COST', 'USED_BEFORE', 'DEFECTS', 'DESELECTED']
weight_FSP = {'COST': 1 / 4, 'USED_BEFORE': 1 / 4, 'DEFECTS': 1 / 4, 'DESELECTED': 1 / 4}

names_NRP = ['classic-1', 'classic-2', 'classic-3']
# names_NRP = ['classic-1']
order_NRP = ['cost', 'revenue']
weight_NRP = {'cost': 1 / 2, 'revenue': 1 / 2}

hymoo_result_folder = 'hymoo'
nsgaii_result_folder = 'nsgaii'
moqa_result_folder = 'moqa'

hysoo_result_folder = 'hysoo'
sa_result_folder = 'sa'
soqa_result_folder = 'soqa'

# compare CQHA with NSGA-II
for name in names_NRP:
    problem = Problem(name)
    problem.vectorize(order_NRP)

    '''prepare the problem result folder before solving'''
    # Multi-objective
    # hymoo_problem_result = ProblemResult(name, problem, hymoo_result_folder)
    # nsgaii_problem_result = ProblemResult(name, problem, nsgaii_result_folder)
    # Single-objective
    sa_problem_result = ProblemResult(name, problem, sa_result_folder)
    hysoo_problem_result = ProblemResult(name, problem, hysoo_result_folder)

    '''Load result'''
    # Multi-objective
    # nsgaii_result = MethodResult('nsgaii', nsgaii_problem_result.path, problem)
    # nsgaii_result.load()
    # hymoo_result = MethodResult('hymoo', hymoo_problem_result.path, problem)
    # hymoo_result.load()
    # Single-objective
    sa_result = MethodResult('sa', sa_problem_result.path, problem)
    sa_result.load(single_flag=True)
    hysoo_result = MethodResult('hysoo', hysoo_problem_result.path, problem)
    hysoo_result.load(single_flag=True)

    '''Add result'''
    # hymoo_problem_result.add(nsgaii_result)
    # hymoo_problem_result.add(hymoo_result)

    hysoo_problem_result.add(hysoo_result)
    hysoo_problem_result.add(sa_result)


    # compare
    # scores_ga = hymoo_problem_result.average_compare(union_method='nsgaii', average_method='hymoo')
    # table_ga = Visualizer.tabulate_single_problem(
    #     name, ['nsgaii', 'hymoo'], ['elapsed time', 'found', 'front', 'igd', 'hv', 'spacing', 'tts'],
    #     scores_ga, {'elapsed time': 4, 'found': 5, 'front': 4, 'igd': 4, 'hv': 4, 'spacing': 4, 'tts': 4}
    # )
    # Visualizer.tabluate(table_ga, 'nsgaii-hymoo-compare-{}.csv'.format(name))

    scores_sa = hysoo_problem_result.statistical_analysis(method1="hysoo", method2="sa", weights=weight_NRP)
    table_sa = Visualizer.tabulate_single_problem(
        name, ['hysoo', 'sa'], ['time', 'statistic', 'p_value', 'mean', 'std', 'max', 'min'],
        scores_sa, {'time': 6, 'statistic': 12, 'p_value': 18, 'mean': 4, 'std': 4, 'max': 4, 'min': 4}
    )
    Visualizer.tabluate(table_sa, 'sa-hysoo-compare-{}.csv'.format(name))

# for name in names_FSP:
#     problem = Problem(name)
#     problem.vectorize(order_FSP)

#     '''prepare the problem result folder before solving'''
#     # Multi-objective
#     hymoo_problem_result = ProblemResult(name, problem, hymoo_result_folder)
#     nsgaii_problem_result = ProblemResult(name, problem, nsgaii_result_folder)
#     # Single-objective
#     # sa_problem_result = ProblemResult(name, problem, sa_result_folder)
#     # hysoo_problem_result = ProblemResult(name, problem, hysoo_result_folder)

#     '''Load result'''
#     # Multi-objective
#     nsgaii_result = MethodResult('nsgaii', nsgaii_problem_result.path, problem)
#     nsgaii_result.load()
#     hymoo_result = MethodResult('hymoo', hymoo_problem_result.path, problem)
#     hymoo_result.load()
#     # Single-objective
#     # sa_result = MethodResult('sa', sa_problem_result.path, problem)
#     # sa_result.load(single_flag=True)
#     # hysoo_result = MethodResult('hysoo', hysoo_problem_result.path, problem)
#     # hysoo_result.load(single_flag=True)

#     '''Add result'''
#     # Multi-objective
#     hymoo_problem_result.add(nsgaii_result)
#     hymoo_problem_result.add(hymoo_result)
#     # Single-objective
#     # hysoo_problem_result.add(hysoo_result)
#     # hysoo_problem_result.add(sa_result)

#     # compare
#     scores_ga = hymoo_problem_result.average_compare(union_method='nsgaii', average_method='hymoo')
#     table_ga = Visualizer.tabulate_single_problem(
#         name, ['nsgaii', 'hymoo'], ['elapsed time', 'found', 'front', 'igd', 'hv', 'spacing', 'tts'],
#         scores_ga, {'elapsed time': 4, 'found': 5, 'front': 4, 'igd': 4, 'hv': 4, 'spacing': 4, 'tts': 4}
#     )
#     Visualizer.tabluate(table_ga, 'nsgaii-hymoo-compare-{}.csv'.format(name))

#     # scores_sa = hysoo_problem_result.statistical_analysis(method1="hysoo", method2="sa", weights=weight_FSP)
#     # table_sa = Visualizer.tabulate_single_problem(
#     #     name, ['hysoo', 'sa'], ['time', 'statistic', 'p_value', 'mean', 'std', 'max', 'min'],
#     #     scores_sa, {'time': 6, 'statistic': 12, 'p_value': 18, 'mean': 4, 'std': 4, 'max': 4, 'min': 4}
#     # )
#     # Visualizer.tabluate(table_sa, 'sa-hysoo-compare-{}.csv'.format(name))

