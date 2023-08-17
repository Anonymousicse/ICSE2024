import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from os.path import join
from typing import List
import json
from csv import reader
from nen.DescribedProblem import DescribedProblem
from nen.util.FSP import DimacsMOIPProblem


def parse_comma_list(line: str) -> List[str]:
    return [e for e in line.strip(' ').split(',') if e]


def load_rp(name: str):
    # prepare the problem
    problem = DescribedProblem()
    # find the data set path
    data_path = join(DescribedProblem.RAW_DATA_PATH, 'NRP/rp/{}'.format(name)).replace('\\', '/')
    # prepare three files
    requirement_file = join(data_path, 'requirements.csv').replace('\\', '/')
    stakeholder_file = join(data_path, 'stakeholders.csv').replace('\\', '/')
    value_file = join(data_path, 'value.csv').replace('\\', '/')
    urgency_file = join(data_path, 'urgency.csv').replace('\\', '/')
    # read requirement file and make cost, couplings and precedes
    tmp_cost = {}
    tmp_couplings = {}
    tmp_precedes = {}
    variables_set = set()
    with open(requirement_file, 'r') as req_file:
        csv = reader(req_file, delimiter='|', skipinitialspace=True)
        for row in csv:
            if not row:
                break
            row = [e.strip(' ') for e in row]
            name, cost, couplings, precedes = row
            assert name not in variables_set
            problem.variables.append(name)
            variables_set.add(name)
            # check name
            assert name not in tmp_cost
            assert name not in tmp_couplings
            assert name not in tmp_precedes
            # add into tmp dicts
            tmp_cost[name] = int(cost)
            tmp_couplings[name] = parse_comma_list(couplings)
            tmp_precedes[name] = parse_comma_list(precedes)
        req_file.close()
    # read stakeholder file and make weight
    tmp_weight = []
    with open(stakeholder_file, 'r') as sh_file:
        csv = reader(sh_file, delimiter='|', skipinitialspace=True)
        for row in csv:
            if not row: break
            tmp_weight.append(int(row[0]))
    weight_sum = sum(tmp_weight)
    # NOTE: weights have been weighted average
    weight = [v / weight_sum for v in tmp_weight]
    # read value file and make revenue
    tmp_revenue = {}
    with open(value_file, 'r') as val_file:
        csv = reader(val_file, delimiter='|', skipinitialspace=True)
        for row in csv:
            if not row: break
            row = [e.strip(' ') for e in row]
            requirement = row[0]
            values = row[1:]
            assert requirement not in tmp_revenue
            assert len(values) == len(weight)
            tmp_revenue[row[0]] = round(sum([int(values[i]) * weight[i] for i in range(len(values))]))
    # read urgency file and make urgency
    tmp_urgency = {}
    with open(urgency_file, 'r') as urg_file:
        csv = reader(urg_file, delimiter='|', skipinitialspace=True)
        for row in csv:
            if not row: break
            row = [e.strip(' ') for e in row]
            requirement = row[0]
            values = row[1:]
            assert requirement not in tmp_urgency
            assert len(values) == len(weight)
            tmp_urgency[row[0]] = round(sum([int(values[i]) * weight[i] for i in range(len(values))]))
    # pack into problem, revenue and urgency should be min form
    problem.objectives['cost'] = {k: float(v) for k, v in tmp_cost.items()}
    problem.objectives['revenue'] = {k: -v for k, v in tmp_revenue.items()}
    problem.objectives['urgency'] = {k: -v for k, v in tmp_urgency.items()}

    problem.objectives['single'] = {k: 0.0 for k in variables_set}
    for k, v in tmp_cost.items():
        problem.objectives['single'][k] += 0.5 * v
    for k, v in tmp_revenue.items():
        problem.objectives['single'][k] -= 0.5 * v

    for requirement, couplings_list in tmp_couplings.items():
        for coupling in couplings_list:
            problem.constraints.append([coupling, '<=>', requirement])
    for requirement, precedes_list in tmp_precedes.items():
        for precede in precedes_list:
            # NOTE: x => y if False iff. x > y
            # if precede is selected, reqiurement must be selected
            problem.constraints.append([precede, '=>', requirement])
    # return
    return problem


def load_fsp(name):
    # prepare the problem
    problem = DescribedProblem()
    # load with DimacsMOIPProblem
    dimacs = DimacsMOIPProblem(name)
    feature_name = dimacs.featureNames
    feature_num = dimacs.featureCount
    problem.variables = list(feature_name.values())
    for objective_index, objective in enumerate(dimacs.objectiveSparseMapList):
        tmp_objective = {feature_name[k]: v for k, v in objective.items()}
        problem.objectives[dimacs.objectNames[objective_index]] = tmp_objective
    for inequation_index, inequation in enumerate(dimacs.sparseInequationsMapList):
        assert dimacs.sparseInequationSensesList[inequation_index] == 'L'
        left = {}
        right = 0
        for k, v in inequation.items():
            if k == feature_num:
                right = v
            else:
                left[feature_name[k]] = v
        problem.constraints.append([left, '<=', right])
    for equation in dimacs.sparseEquationsMapList:
        left = {}
        right = 0
        for k, v in equation.items():
            if k == feature_num:
                right = v
            else:
                left[feature_name[k]] = v
        problem.constraints.append([left, '=', right])
    return problem


def load_fsp_new(name):
    # prepare input files
    dimacs_file_name = join(DescribedProblem.RAW_DATA_PATH, 'FSP/{}.dimacs'.format(name)).replace('\\', '/')
    augment_file_name = join(DescribedProblem.RAW_DATA_PATH, 'FSP/{}.dimacs.augment'.format(name)).replace('\\', '/')
    new_file_name = join(DescribedProblem.RAW_DATA_PATH, 'FSP/{}.dimacs.new'.format(name)).replace('\\', '/')
    dead_file_name = join(DescribedProblem.RAW_DATA_PATH, 'FSP/{}.dimacs.dead'.format(name)).replace('\\', '/')
    mandatory_file_name = \
        join(DescribedProblem.RAW_DATA_PATH, 'FSP/{}.dimacs.mandatory'.format(name)).replace('\\', '/')
    # prepare problem
    problem = DescribedProblem()
    # read features from old dimacs file
    feature_name = {}
    with open(dimacs_file_name, 'r') as dimacs_file:
        # c <index> <feature name>
        for line in dimacs_file:
            line = line.strip()
            if line == '': continue
            if line.startswith('p cnf '): break
            parts = line.split(' ')
            if parts[1].endswith('$'):
                parts[1] = parts[1].replace('$', '')
            if parts[0] == 'c' and parts[1].isnumeric():
                index = int(parts[1].strip())
                name = parts[2].strip()
                feature_name[index] = name
                problem.variables.append(name)
    # read inequations from .new file
    feature_num = 0
    inequations_num = 0
    inequations = []
    with open(new_file_name, 'r') as new_file:
        for line in new_file:
            line = line.strip()
            if line == '': continue
            parts = line.split(' ')
            if line.startswith('p cnf '):
                feature_num = int(parts[2].strip())
                inequations_num = int(parts[3].strip())
            else:
                parts = [int(x.strip()) for x in parts if x.strip() != '']
                assert parts[-1] == 0
                if len(parts) == 3 and (parts[0] < 0 or parts[1] < 0):
                    # NOTE: might be dependency or exclude
                    if parts[0] < 0 and parts[1] < 0:
                        # exclude
                        inequations.append([feature_name[-parts[0]], '><', feature_name[-parts[1]]])
                    elif parts[0] > 0 and parts[1] < 0:
                        inequations.append([feature_name[-parts[1]], '=>', feature_name[parts[0]]])
                    elif parts[0] < 0 and parts[1] > 0:
                        inequations.append([feature_name[-parts[0]], '=>', feature_name[parts[1]]])
                else:
                    # -xn1 -xn2 ... xp1 xp2 ... 0 denotes
                    # sum(1 - xni) + sum(xpi) >= 1
                    # equals to: sum(-xpi) + sum(xni) <= count(xni) - 1
                    # if len(parts) >= 3:
                    #     inequations_num -= 1
                    #     continue
                    negative_count = sum(map(lambda x: 1 if x < 0 else 0, parts[:-1]))
                    tmp_coef = {}
                    for feature in parts[:-1]:
                        feature_index = int(feature)
                        assert feature_index != 0
                        if feature_index > 0:
                            tmp_coef[feature_name[int(feature)]] = -1
                        else:
                            tmp_coef[feature_name[-int(feature)]] = 1
                    inequations.append([tmp_coef, '<=', negative_count - 1])
    assert len(inequations) == inequations_num
    assert len(feature_name) == feature_num
    problem.constraints.extend(inequations)
    # read mandatory features from mandatory file
    with open(mandatory_file_name, 'r') as mandatory_file:
        for line in mandatory_file:
            line = line.strip()
            if line == '': continue
            if line.isnumeric():
                # feature: 1 = 1
                problem.constraints.append([{feature_name[int(line)]: 1}, '=', 1])
    # read dead features from dead file
    with open(dead_file_name, 'r') as dead_file:
        for line in dead_file:
            line = line.strip()
            if line == '': continue
            if line.isnumeric():
                # feature: 1 = 0
                problem.constraints.append([{feature_name[int(line)]: 1}, '=', 0])
    # read objectives from augments file
    objective_name = {}
    objectives = {}
    with open(augment_file_name, 'r') as augment_file:
        for line in augment_file:
            line = line.strip()
            if line == '': continue
            if line.startswith('#FEATURE_INDEX '):
                # initialize objectives
                attributes = line.split(' ')
                for i in range(1, len(attributes)):
                    objective_name[i] = attributes[i]
                    objectives[attributes[i]] = {}
            else:
                parts = line.split(' ')
                assert len(parts) == (len(objective_name) + 1)
                for i in range(1, len(parts)):
                    objectives[objective_name[i]][feature_name[int(parts[0])]] = float(parts[i])
    problem.objectives = objectives
    # used before should be 1 - x
    problem.objectives['USED_BEFORE'] = {k: 1 - v for k, v in problem.objectives['USED_BEFORE'].items()}
    # add another objectives, deselect
    problem.objectives['DESELECTED'] = {k: -1 for k in problem.variables}
    # problem.objectives['DESELECTED'] = {k: -10 for k in problem.variables}
    return problem


def parse_colon_line(line):
    colon_splited = line.strip().split(':')
    assert len(colon_splited) == 2
    head, tail = colon_splited
    if not tail: return head, []
    tail = tail.strip().split(' ')
    return head, tail


def load_tsm(name):
    # prepare Problem
    problem = DescribedProblem()
    # prepare input path
    data_path = join(DescribedProblem.RAW_DATA_PATH, 'TSM/{name}_v5/{type}.info').replace('\\', '/')
    # load rtime
    tmp_rtime = {}
    with open(data_path.format(name=name, type='rtime'), 'r') as rtime_file:
        for line in rtime_file:
            if not line: continue
            testcase, rtimes = parse_colon_line(line)
            tmp_rtime[testcase] = int(rtimes[0])
    # load fault
    tmp_fault = {}
    with open(data_path.format(name=name, type='fault'), 'r') as fault_file:
        for line in fault_file:
            if not line: continue
            testcase, faults = parse_colon_line(line)
            for fault in faults:
                fault_name = 'f' + fault
                tmp_fault[fault_name] = tmp_fault.get(fault_name, []) + [testcase]
    # load coverage
    tmp_statement = {}
    with open(data_path.format(name=name, type='cov'), 'r') as cov_file:
        for line in cov_file:
            if not line: continue
            testcase, statements = parse_colon_line(line)
            for statement in statements:
                statement_name = 's' + statement
                tmp_statement[statement_name] = tmp_statement.get(statement_name, []) + [testcase]
    # variables
    problem.variables = list(tmp_rtime.keys()) + list(tmp_fault.keys())
    # pack into problem, fault is a max obj, thus need negating
    problem.objectives['rtime'] = tmp_rtime
    problem.objectives['fault'] = {k: -1 for k in tmp_fault}
    for fault, testcases in tmp_fault.items():
        problem.constraints.append([testcases, 'or', fault])
    # NOTE: Instead of use statements, we convert "statement coverage" object as a constraint
    # which means all statements should be covered at least once.
    # test case t1, ..., ti, ... or sj => Sum ti >= 1 => Sum -ti <= -1
    for _, testcases in tmp_statement.items():
        problem.constraints.append([{t: -1 for t in testcases}, '<=', '-1'])
    return problem


def flatten(constraints):
    class Node:
        def __init__(self, name):
            self.name = name
            self.in_degree = 0
            self.out = []

    def find_dependency(nodes, name):
        deps = []
        for d in nodes[name].out:
            deps.append(d)
            deps += find_dependency(nodes, d)
        return deps

    nodes = {}
    for constraint in constraints:
        assert isinstance(constraint, list)
        assert len(constraint) == 3
        x, sense, y = constraint
        assert sense == '=>'
        if x not in nodes:
            nodes[x] = Node(x)
        if y not in nodes:
            nodes[y] = Node(y)
        nodes[x].out.append(y)
        nodes[y].in_degree += 1
    node_list = []
    for name, node in nodes.items():
        if node.in_degree == 0:
            node.out = find_dependency(nodes, name)
            node_list.append(node)

    new_constraints = []
    for node in node_list:
        if node.name.startswith('r'): continue
        for d in node.out:
            new_constraints.append([node.name, '=>', d])
    return new_constraints


def load_xuan(name):
    # prepare Problem
    problem = DescribedProblem()
    # prepare input path
    assert isinstance(name, str)
    data_path = join(DescribedProblem.RAW_DATA_PATH, 'NRP', 'xuan')
    if name.startswith('classic'):
        file_name = join(data_path, 'classic-nrp', 'nrp{}.txt'.format(name[len('classic-'):]))
    elif name.startswith('realistic'):
        file_name = join(data_path, 'realistic-nrp', 'nrp{}.txt'.format(name[len('realistic'):]))
    else:
        assert False
    # read file
    cost, revenue, urgency = {}, {}, {}
    requirement_count = 0
    stakeholder_count = 0
    with open(file_name, 'r') as nrp_file:
        # level of requirements
        level = int(nrp_file.readline())
        for _ in range(level):
            # requirements in current level
            requirements_num = int(nrp_file.readline())
            # read requirements costs in current level
            line_cost = [int(x) for x in nrp_file.readline().strip().split(' ') if x != '']
            assert requirements_num == len(line_cost)
            for c in line_cost:
                requirement_count += 1
                cost['r{}'.format(requirement_count)] = c
                problem.variables.append('r{}'.format(requirement_count))
        # dependencies
        dependencies_num = int(nrp_file.readline())
        for _ in range(dependencies_num):
            dependency = [x for x in nrp_file.readline().strip().split(' ') if x != '']
            assert len(dependency) == 2
            # problem.constraints.append(['r{}'.format(dependency[1]), '=>', 'r{}'.format(dependency[0])])
            problem.constraints.append(['r{}'.format(dependency[1]), '=>', 'r{}'.format(dependency[0])])
        assert dependencies_num == len(problem.constraints)
        # read customers
        customers_num = int(nrp_file.readline())
        for _ in range(customers_num):
            line = [int(x) for x in nrp_file.readline().strip().split(' ') if x != '']
            stakeholder_count += 1
            stakeholder = 's{}'.format(stakeholder_count)
            problem.variables.append(stakeholder)
            revenue[stakeholder] = line[0]
            require_num = line[1]
            require_list = line[2:]
            assert len(require_list) == require_num
            for req in require_list:
                problem.constraints.append([stakeholder, '=>', 'r{}'.format(req)])
    # read urgency
    urgency_file_name = join(data_path, 'urgency', '{}.json'.format(name))
    with open(urgency_file_name, 'r') as urgency_file:
        content = json.load(urgency_file)
        assert isinstance(content, list)
        assert len(content) == requirement_count
        for req, urg in enumerate(content):
            urgency['r{}'.format(req + 1)] = urg
    # construct objectives
    problem.objectives['cost'] = cost
    # problem.objectives['cost'] = {k: v for k, v in cost.items()}
    problem.objectives['revenue'] = {k: -v for k, v in revenue.items()}
    problem.objectives['urgency'] = {k: -v for k, v in urgency.items()}
    # flatten constraints
    problem.constraints = flatten(problem.constraints)
    return problem


def load_Baan():
    problem = DescribedProblem()
    requirement_num = 100
    team_num = 17
    file_name = join(DescribedProblem.RAW_DATA_PATH, 'NRP', 'Baan', 'Baan_core.csv')
    # variables
    for req in range(requirement_num):
        requirement = 'r{}'.format(req + 1)
        problem.variables.append(requirement)
    # cost per team
    team_list = [{} for _ in range(team_num)]
    # cost, revenue, urgency
    cost, revenue, urgency = {}, {}, {}
    with open(file_name, 'r') as baan_file:
        csv = reader(baan_file, delimiter=',', skipinitialspace=True)
        req = 0
        for line in csv:
            if req < requirement_num:
                requirement = 'r{}'.format(req + 1)
                line = [int(x) for x in line]
                assert len(line) == (team_num + 3)
                # cost per team
                for team in range(team_num):
                    if line[team] > 0:
                        team_list[team][requirement] = line[team]
                # cost sum, revenue, urgency
                cost[requirement] = line[-3]
                revenue[requirement] = line[-2]
                urgency[requirement] = line[-1]
            else:
                for team in range(team_num):
                    problem.constraints.append([team_list[team], '<=', int(line[team])])
            req += 1
    # objectives
    problem.objectives['cost'] = cost
    problem.objectives['revenue'] = {k: -v for k, v in revenue.items()}
    problem.objectives['urgency'] = {k: -v for k, v in urgency.items()}
    return problem


if __name__ == '__main__':
    # FSP
    fsp_problems = ['eCos']
    for fsp_name in fsp_problems:
        problem = load_fsp_new(fsp_name)
        problem.dump(fsp_name)
    # # NRP: rp
    # rp_problems = ['ms', 'rp']
    # for rp_name in rp_problems:
    #     problem = load_rp(rp_name)
    #     problem.dump(rp_name + '_single')
    # # TSM
    # tsm_problems = ['make']
    # for tsm_name in tsm_problems:
    #     problem = load_tsm(tsm_name)
    #     problem.dump(tsm_name)
    # NRP: Xuan
    # xuan = ['classic-1', 'classic-2', 'classic-3', 'classic-4', 'classic-5',
    #         'realistic-e1', 'realistic-e2', 'realistic-e3', 'realistic-e4',
    #         'realistic-g1', 'realistic-g2', 'realistic-g3', 'realistic-g4',
    #         'realistic-m1', 'realistic-m2', 'realistic-m3', 'realistic-m4'
    #         ]
    # xuan = ['classic-3']
    # for xuan_name in xuan:
    #     problem = load_xuan(xuan_name)
    #     problem.dump(xuan_name)
    # # NRP: Baan
    # problem = load_Baan()
    # problem.dump('Baan')
