from typing import List, Dict, Any, Optional, Tuple, Set
from os import path
from pathlib import Path
from scipy import stats
import json
import numpy
import copy
import numpy as np


from nen.Problem import Problem
from nen.util.util import RESULT_ROOT
from nen.util.evenness_indicator import EvennessIndicator
from jmetal.util.archive import NonDominatedSolutionsArchive
from jmetal.core.solution import BinarySolution
from jmetal.core.quality_indicator import InvertedGenerationalDistance, HyperVolume
import math


class NDArchive:
    """ [summary] NDArchive, short for Non Dominated (Solution) Archive, maintain a pareto solution set.
    It is initialized with variables num and objectives num.
    """
    # config
    ROUND_PRECISION = 2

    def __init__(self, variables_num: int, objectives_num: int):
        # record the number of variables and objectives
        self.variables_num: int = variables_num
        self.objectives_num: int = objectives_num
        # the archive
        self.archive = NonDominatedSolutionsArchive()
        self.all_solution_num: float = 0.0
        self.total_num_anneals = 0
        self.iterations = 0
        self.feasible_num = 0

    def add(self, solution: BinarySolution) -> bool:
        """add [summary] add a non-dominant solution into nd archive.
        """
        # check whether solution is feasible
        if solution is None:
            return False
        if sum(solution.constraints) > 0:
            return False
        # check variables size and objectives size
        assert len(solution.variables[0]) == self.variables_num
        assert len(solution.objectives) == self.objectives_num
        # round objectives with NDArchive.ROUND_PRECISION
        solution.objectives = [round(x, NDArchive.ROUND_PRECISION) for x in solution.objectives]
        self.all_solution_num += 1
        return self.archive.add(solution)
        # self.solution_list.append(solution)
        # return True

    def wso_add(self, solution: BinarySolution) -> bool:
        """add [summary] add a solution in a single problem into nd archive.
        """
        # check wether solution is feasible
        if solution is None:
            return False
        if sum(solution.constraints) > 0:
            return False
        # check variables size and objectives size
        assert len(solution.variables[0]) == self.variables_num
        assert len(solution.objectives) == self.objectives_num
        # round objectives with NDArchive.ROUND_PRECISION
        solution.objectives = [round(x, NDArchive.ROUND_PRECISION) for x in solution.objectives]
        if solution not in self.solution_list:
            self.feasible_num += 1
        self.solution_list.append(solution)
        
        return True

    def set_solution_list(self, solution_list: List[BinarySolution]) -> None:
        """set_solution_list [summary] set solutions directly without any checks.
        """
        self.archive.solution_list = solution_list

    def __len__(self) -> int:
        return len(self.archive.solution_list)

    @staticmethod
    def dominate(s1: BinarySolution, s2: BinarySolution) -> bool:
        equal = True
        for i, o1 in enumerate(s1.objectives):
            o1 = round(o1, NDArchive.ROUND_PRECISION)
            o2 = round(s2.objectives[i], NDArchive.ROUND_PRECISION)
            if o1 > o2: return False
            elif o1 < o2:
                equal = False
        return not equal

    @property
    def solution_list(self) -> List[BinarySolution]:
        """solution_list [summary] return the list of solutions
        """
        return self.archive.solution_list

    @staticmethod
    def bool_list_to_str(bool_list: List[bool]) -> str:
        """bool_list_to_str [summary] convert bool list to a 0/1 string.
        """
        return ''.join(['1' if element else '0' for element in bool_list])

    @staticmethod
    def str_to_bool_list(zero_one_str: str) -> List[bool]:
        """str_to_bool_list [summary] convert a 0/1 string to bool list.
        """
        return [True if element == '1' else False for element in zero_one_str]

    @staticmethod
    def float_list_to_str(float_list: List[float]) -> str:
        """float_list_to_str [summary] convert a float list to a string.
        """
        return ' '.join([str(round(element, NDArchive.ROUND_PRECISION)) for element in float_list])

    @staticmethod
    def str_to_float_list(float_list_str: str) -> List[float]:
        """str_to_float_list [summary] convert str to float list.
        """
        return [float(element) for element in float_list_str.strip().split() if element]


class Result(NDArchive):
    """Result [summary] Result corresponds with the class Problem, it manages the solutions,
    elapsed time and other information with a single solving on a Problem.
    """
    def __init__(self, problem: Problem) -> None:
        super().__init__(problem.variables_num, problem.objectives_num)
        self.elapsed: float = 0.0
        self.info: Dict[str, Any] = {}

    @property
    def single(self) -> Optional[BinarySolution]:
        """single [summary] use Result as a single solution.
        """
        if len(self.solution_list) == 0:
            return None
        else:
            return self.solution_list[0]

    def get_wso_objective(self, weights: List[float]) -> List[float]:
        """get_wso_objective [summary] calculate the wso_objective as result of single-objective
        """
        # if len(self.solution_list) == 0:
        #     return [float('inf')]
        objective = []
        for solution in self.solution_list:
            assert len(solution.objectives) == len(weights)
            obj = 0.0
            for i in range(solution.number_of_objectives):
                
                obj += (solution.objectives[i] * weights[i])
            objective.append(obj)
        return objective


class MethodResult:
    """ [summary] MethodResult is a record for a ceratin method solving on a certain problem
    with 1 or more iterations. It would record method parameters, solving elapsed time(s) and archive(s).

    Note that, one MethodResult might contain serveral archives and so on for iteration > 1.
    """
    def __init__(self, name: str, parent_path: str, problem: Problem) -> None:
        self.name: str = name
        self.parent_path: str = parent_path
        self.path: str = path.join(parent_path, name)
        self.problem: Problem = problem
        self.iteration: int = 0
        self.info: Dict[str, Any] = {}

        self.method_result: Optional[Result] = None
        self.results: List[Result] = []

    def obj_file_name(self, index: int) -> str:
        return path.join(self.path, '{}.obj.txt'.format(index))

    def var_file_name(self, index: int) -> str:
        return path.join(self.path, '{}.var.txt'.format(index))

    def info_file_name(self) -> str:
        return path.join(self.path, '{}.info.json'.format(self.name))

    def add(self, result: Result) -> None:
        """add [summary] add a result in MethodResult.
        """
        self.iteration += 1
        self.results.append(result)

    def get_wso_objective(self, weights: List[float]) -> List[float]:
        """get_wso_objective [summary] calculate the wso_objective as result of single-objective
        """
        objective = []
        for solution in self.method_result.solution_list:
            assert len(solution.objectives) == len(weights)
            obj = 0.0
            for i in range(solution.number_of_objectives):
                obj += (solution.objectives[i] * weights[i])
            objective.append(obj)
        return objective

    def get_result(self, index: int) -> Result:
        """get_archive [summary] get the certain Result within the iteration.
        """
        return self.results[index]

    def get_solution_list(self, index: int) -> List[BinarySolution]:
        """get_solution_list [summary] get the certain solution list of an archive with given index.
        """
        return self.get_result(index).solution_list

    def get_method_result(self) -> Optional[Result]:
        """get_method_result [summary] get the method result, remember to make method result first.
        """
        return self.method_result

    def get_method_solution_list(self) -> List[BinarySolution]:
        """get_method_solution_list [summary] get the method solution list.
        """
        if self.method_result is not None:
            return self.method_result.solution_list
        else:
            return []

    def get_elapseds(self) -> List[float]:
        """get_elapseds [summary] get elapseds time for each iteration.
        """
        return [result.elapsed for result in self.results]

    def make_method_result(self, single_flag: bool = False) -> None:
        """make_method_result [summary] make the method result with all solutions of every archives.
        single_flag: a flag to whether judgment is a sign of a single-objective problem
        """
        # initialize method result
        self.method_result = Result(self.problem)
        # add each solution and count up the elapsed time
        self.method_result.total_num_anneals = 0
        self.method_result.iterations = 0
        for result in self.results:
            self.method_result.elapsed += result.elapsed
            self.method_result.iterations += result.iterations
            self.method_result.total_num_anneals += result.total_num_anneals
            if single_flag:
                for solution in result.solution_list:
                    self.method_result.solution_list.append(solution)
            else:
                for solution in result.solution_list:
                    self.method_result.add(solution)
                    self.method_result.all_solution_num += 1

    def dump_result(self, index: int) -> None:
        """dump_result [summary] dump the result archive into .obj and .var files
        (which contain objectives and variables according to the same order).
        """
        # check dump path
        assert path.isdir(self.path)
        # prepare ordered objectives, sorted by first value in objectives
        solutions = self.get_solution_list(index)
        if solutions is not None:
            solutions.sort(key=lambda x: x.objectives[0])
        # dump objectives
        with open(self.obj_file_name(index), 'w+') as obj_file:
            if solutions is None:
                obj_file.write('Nan' + '\n')
            else:
                for solution in solutions:
                    obj_file.write(NDArchive.float_list_to_str(solution.objectives) + '\n')
        # dump variables
        with open(self.var_file_name(index), 'w+') as var_file:
            if solutions is None:
                obj_file.write('Nan' + '\n')
            else:
                for solution in solutions:
                    var_file.write(NDArchive.bool_list_to_str(solution.variables[0]) + '\n')

    def load_result(self, index: int, evaluate: bool = False, single_flag: bool = False) -> None:
        """load_result [summary] load the result with archive (objectives and variables) from files (.obj and .var).
        It would involve problem information, thus need a problem.

        If evaluate is True, solutions would be loaded from variables via problem.evaluate.
        It would check if a solution is feasible and it still loads objectives but just for checking.
        If the evaluate is False, then solutions are loaded form both variables and objectives,
        at the same time, assume the solutions is feasible.
        """
        # prepare load files
        assert path.isdir(self.path)
        assert path.isfile(self.obj_file_name(index))
        assert path.isfile(self.var_file_name(index))
        # check index
        assert index == len(self.results)
        # prepare the variables list and objectives list
        variables_list: List[List[bool]] = []
        objectives_list: List[List[float]] = []
        # load variables
        with open(self.var_file_name(index), 'r') as var_file:
            for line in var_file:
                if line.strip() == '': continue
                variables = NDArchive.str_to_bool_list(line.strip())
                assert len(variables) == self.problem.variables_num
                variables_list.append(variables)
        # load objectives
        with open(self.obj_file_name(index), 'r') as obj_file:
            for line in obj_file:
                if line.strip() == '': continue
                objectives = NDArchive.str_to_float_list(line.strip())
                if not single_flag:
                    assert len(objectives) == self.problem.objectives_num
                objectives_list.append(objectives)
        assert len(objectives_list) == len(variables_list)
        # prepare list of BinarySolution
        solution_list: List[BinarySolution] = []
        if evaluate:
            for index in range(len(variables_list)):
                values = {self.problem.variables[i]: variables_list[index][i]
                          for i in range(self.problem.variables_num)}
                solution = self.problem.evaluate(values)
                # assert solution.constraints[0] == 0
                if solution.constraints[0] != 0:
                    continue
                # for i in range(self.problem.objectives_num):
                #     assert round(solution.objectives[i], NDArchive.ROUND_PRECISION) == objectives_list[index][i]
                solution_list.append(solution)
        else:
            for index in range(len(variables_list)):
                solution = self.problem._empty_solution()
                solution.variables = [variables_list[index]]
                solution.objectives = objectives_list[index]
                if self.problem.constraints_num > 0:
                    solution.constraints[0] = 0
                solution_list.append(solution)
        # append to archives
        result = Result(self.problem)
        result.all_solution_num = 0
        # archive.set_solution_list(solution_list)
        if single_flag:
            for solution in solution_list:
                result.wso_add(solution)
        else:
            for solution in solution_list:
                result.add(solution)
                # result.all_solution_num += 1
        self.results.append(result)

    def dump_info(self) -> None:
        """dump_info [summary] dump all info (except for solutions) into a json file
        """
        # write elapeds into info
        self.info['iteration'] = len(self.results)
        self.info['elapseds'] = [result.elapsed for result in self.results]
        self.info['total_num_anneals'] = [result.total_num_anneals for result in self.results]
        # dump into file
        with open(self.info_file_name(), 'w+') as info_out:
            json.dump(self.info, info_out)
            info_out.close()

    def load_info(self) -> Tuple[int, List[float]]:
        """load_info [summary] load info from file, return iteration number and elapseds.
        """
        with open(self.info_file_name(), 'r') as info_in:
            self.info = json.load(info_in)
            info_in.close()
        return self.info['iteration'], self.info['elapseds'], self.info['total_num_anneals']

    def dump(self) -> None:
        """dump [summary] dump achives (<index>.obj.txt, <index>.var.txt) and info (.info.json).
        """
        # prepare folder
        Path(self.path).mkdir(parents=True, exist_ok=True)
        # dump info file
        self.dump_info()
        # dump archives
        for index in range(self.info['iteration']):
            self.dump_result(index)

    def load(self, evaluate: bool = True, single_flag: bool = False) -> None:
        """load [summary] load the MethodResult from files, indicated by info file.
        Evaluate is True as we want to load solutions from variables via evaluation.
        """
        print(self.path)
        # check folder
        assert path.isdir(self.path)
        # load info
        self.iteration, elapseds, total_num_anneals = self.load_info()
        assert len(elapseds) == self.iteration
        # load results
        for index in range(self.iteration):
            self.load_result(index, evaluate, single_flag)
            self.results[index].elapsed = elapseds[index]
            self.results[index].total_num_anneals = total_num_anneals[index]
        assert len(self.results) == self.iteration


class HashableObjectives:
    """ [summary] HashableObjectives is a hashable term for float list.
    """
    def __init__(self, solution: BinarySolution) -> None:
        self.objectives = [round(x, NDArchive.ROUND_PRECISION) for x in solution.objectives]
        self.code = hash(tuple([int(x) for x in self.objectives]))

    def __hash__(self) -> int:
        return self.code

    def __eq__(self, another: object) -> bool:
        if not isinstance(another, HashableObjectives): return False
        if self.__hash__() != another.__hash__(): return False
        for ind, obj in enumerate(self.objectives):
            if round(obj, NDArchive.ROUND_PRECISION) != round(another.objectives[ind], NDArchive.ROUND_PRECISION):
                return False
        return True


class ProblemArchive:
    """ [summary] ProblemArchive presents the pareto front of the problem,
    made up by solutions in every solving results' archives.
    """
    indicators = ['igd', 'hv', 'sp']

    def __init__(self, problem: Problem, method_archives: Dict[str, Result]) -> None:
        """__init__ [summary] ProblemArchive is initialized by the problem and archives.
        """
        self.problem: Problem = problem
        self.method_archives: Dict[str, Result] = method_archives
        self.archive: NDArchive = NDArchive(problem.variables_num, problem.objectives_num)
        self.objectives_set: Set[HashableObjectives] = set()

        # make pareto front from each archive
        for result in method_archives.values():
            for solution_ in result.solution_list:
                self.archive.add(copy.copy(solution_))
        # make objective set
        for solution in self.archive.solution_list:
            self.objectives_set.add(HashableObjectives(solution))

        # convert to ndarray
        self.archive_array: numpy.ndarray = ProblemArchive.archive_to_array(self.archive)
        self.method_archives_array: Dict[str, numpy.ndarray] = \
            {k: ProblemArchive.archive_to_array(v) for k, v in self.method_archives.items()}

    @staticmethod
    def archive_to_array(archive: NDArchive) -> numpy.ndarray:
        return numpy.array([archive.solution_list[i].objectives for i in range(len(archive))])

    def solutions_count(self) -> Dict[str, int]:
        """solutions_count [summary] count how many solutions in each solving results.
        """
        return {k: len(v.solution_list) for k, v in self.method_archives.items()}

    def on_pareto_count(self) -> Dict[str, int]:
        """on_pareto_count [summary] count how many solutions are on problem pareto front
        from each solving result.
        """
        counter: Dict[str, int] = {}
        for obj_name, result in self.method_archives.items():
            counter[obj_name] = 0
            for solution in result.solution_list:
                if HashableObjectives(solution) in self.objectives_set:
                    counter[obj_name] += 1
        return counter

    def p_solve(self) -> Dict[str, float]:
        """p_solve [summary] calculate the probability of solving a problem
        """
        pareto_count = self.on_pareto_count()
        return {k: pareto_count[k] / v.total_num_anneals for k, v in self.method_archives.items()}
        # return {k: len(v.solution_list) / v.total_num_anneals for k, v in self.method_archives.items()}
        # return {k: v.all_solution_num / v.total_num_anneals for k, v in self.method_archives.items()}

    def scale_objective(self, objectives: List[float]) -> List[float]:
        sum_: float = 0.0
        for v in objectives:
            sum_ += v
        sum_ = max(sum_, 1)
        scale_obj: List[float] = []
        for v in objectives:
            scale_obj.append(v / sum_)
        return scale_obj

    def reference_point(self) -> List[float]:
        """reference_point [summary] find the reference point from pareto front, not all found solutions.
        """
        solutions = self.archive.solution_list
        reference_point = []
        for ite in range(self.problem.objectives_num):
            reference_point.append((max([solutions[i].objectives[ite] for i in range(len(solutions))]) * 1.5) / self.problem.each_objevtive_sum[ite] + 0.4)
        return reference_point


    def compute_igd(self) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        for name, solutions in self.method_archives_array.items():
            if len(solutions) < 1: scores[name] = -1.0
            else: scores[name] = InvertedGenerationalDistance(self.archive_array).compute(solutions)
        return scores

    # def compute_hv(self) -> Dict[str, float]:
    #     reference_point = self.reference_point()
    #     scores: Dict[str, float] = {}
    #     for name, solutions in self.method_archives_array.items():
    #         scores[name] = HyperVolume(reference_point).compute(solutions)
    #     return scores
    def compute_hv(self) -> Dict[str, float]:
        reference_point = self.reference_point()
        scores: Dict[str, float] = {}
        for name, solutions in self.method_archives_array.items():
            scaled_solutions = solutions.copy()
            for i in range(len(solutions)):
                solution = solutions[i]
                assert len(solution) == self.problem.objectives_num
                for j in range(len(solution)):
                    scaled_solutions[i][j] = solution[j] / self.problem.each_objevtive_sum[j]
            scores[name] = HyperVolume(reference_point).compute(scaled_solutions)
        return scores

    def compute_sp(self) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        for name, solutions in self.method_archives_array.items():
            scores[name] = EvennessIndicator(self.archive_array).compute(solutions)
        return scores

    def compute_tts(self) -> Dict[str, float]:
        # reference_point = self.reference_point()
        scores: Dict[str, float] = {}
        p_solve = self.p_solve()

        for name, res in self.method_archives.items():
            # assert 0 <= p_solve[name] <= 1
            if p_solve[name] == 0:
                # scores[name] = math.inf
                scores[name] = 0
            elif p_solve[name] == 1:
                scores[name] = 0
            else:
                scores[name] = (math.log(1 - 0.99) / math.log(1 - p_solve[name])) * res.elapsed

        return scores

    def compute(self, indicators: List[str]) -> List[Dict[str, float]]:
        results: List[Dict[str, float]] = []
        for indicator in indicators:
            results.append(getattr(self, 'compute_{}'.format(indicator))())
        return results

    def compute_all(self) -> List[Dict[str, float]]:
        return self.compute(ProblemArchive.indicators)


class ProblemResult:
    """ [summary] ProblemResult is a result manager for a problem solved with one or several solvers.
    It provids methods for load/dump files, prepare problem archives, and compute scores on them.
    """
    def __init__(self, name: str, problem: Problem, result_path: str = '') -> None:
        self.name: str = name
        self.path: str = ''
        if result_path == '':
            self.path = path.join(RESULT_ROOT, self.name)
        else:
            self.path = path.join(RESULT_ROOT, result_path, self.name)
        self.problem: Problem = problem

        self.methods_results: Dict[str, MethodResult] = {}

    def method_result(self, method_name: str) -> MethodResult:
        """method_result [summary] generate a method result with given name and inside this problem result.
        """
        return MethodResult(method_name, self.path, self.problem)

    def add(self, method_result: MethodResult) -> None:
        """add [summary] add a MethodResult into Problem Result
        """
        method_name = method_result.name
        assert method_name not in self.methods_results
        self.methods_results[method_name] = method_result

    def dump(self) -> None:
        """dump [summary] dump to files.
        """
        Path(self.path).mkdir(parents=True, exist_ok=True)
        for result in self.methods_results.values():
            result.dump()

    def load(self, methods: List[str], evaluate: bool = True) -> None:
        """load [summary] load from a folder with the same name.
        """
        assert path.isdir(self.path)
        # load method results with their names
        for method in methods:
            self.methods_results[method] = MethodResult(method, self.path, self.problem)
            self.methods_results[method].load(evaluate)
            # self.methods_results[method].make_method_result(single_flag=True)

    @staticmethod
    def average_of_dicts(scores: List[Dict[str, float]]) -> Dict[str, float]:
        if len(scores) == 0:
            return {}
        result: Dict[str, float] = {key: 0.0 for key in scores[0]}
        for score in scores:
            for key in result:
                if score[key] < 0:
                    continue
                result[key] += score[key]
        iteration = len(scores)
        for key in result:
            result[key] /= iteration
        return result
    
    @staticmethod
    def sum_of_dicts(scores: List[Dict[str, float]]) -> Dict[str, float]:
        if len(scores) == 0:
            return {}
        result: Dict[str, float] = {key: 0.0 for key in scores[0]}
        for score in scores:
            for key in result:
                result[key] += score[key]
        return result

    def statistical_analysis(self, method1: str, method2: str, weights: Dict[str, float], alternative: str = "two-sided"):
        """
        p_value [summary] return statistical analysis of two solutions with two different methods indicated by
        [statistic: float, p_value: float, mean: float, std: float, max: float: min: float].

        alternative: str
        -------
        * 'two-sided': one of the distributions (underlying `x` or `y`) is
          stochastically greater than the other.
        * 'less': the distribution underlying `x` is stochastically less
          than the distribution underlying `y`.
        * 'greater': the distribution underlying `x` is stochastically greater
          than the distribution underlying `y`.
        """
        assert method1 in self.methods_results
        assert method2 in self.methods_results
        method1_result = self.methods_results[method1]
        method2_result = self.methods_results[method2]
        if method1_result.method_result is None:
            method1_result.make_method_result(single_flag=True)
        if method2_result.method_result is None:
            method2_result.make_method_result(single_flag=True)
        # 'alternative' is Alternative Hypothesis
        iteration1 = method1_result.iteration
        iteration2 = method2_result.iteration
        w = []
        for k, v in weights.items():
            w.append(v)

        # calculate
        feasible_num: List[Dict[str, float]] = []
        elapsed: List[Dict[str, float]] = []
        statistics: List[Dict[str, float]] = []
        pvalues: List[Dict[str, float]] = []
        mean: List[Dict[str, float]] = []
        std: List[Dict[str, float]] = []
        max_num: List[Dict[str, float]] = []
        min_num: List[Dict[str, float]] = []
        iteration = max(iteration1, iteration2)
        for i in range(iteration):
            index1 = i % iteration1
            index2 = i % iteration2
            method1_objective = method1_result.results[index1].get_wso_objective(w)
            method2_objective = method2_result.results[index2].get_wso_objective(w)
            if len(method1_objective) == 0:
                method1_objective = [-1 for _ in range(30)]
            if len(method2_objective) == 0:
                method2_objective = [-1 for _ in range(30)]
            # N/A indicates ‘‘not applicable’’ which means that the corresponding
            # algorithm could not statistically compare with itself in the rank-sum test
            # N/A means itself for Wilcoxon’s ranksums p_value
            feasible_num.append({method1: method1_result.results[index1].feasible_num, method2: method2_result.results[index2].feasible_num})
            statistic, pvalue = stats.ranksums(np.array(method1_objective), np.array(method2_objective), alternative=alternative)
            statistics.append({method1: statistic, method2: statistic})
            pvalues.append({method1: pvalue, method2: pvalue})
            mean.append({method1: np.mean(method1_objective), method2: np.mean(method2_objective)})
            std.append({method1: np.std(method1_objective), method2: np.std(method2_objective)})
            max_num.append({method1: np.max(method1_objective), method2: np.max(method2_objective)})
            min_num.append({method1: np.min(method1_objective), method2: np.min(method2_objective)})
            elapsed.append({method1: method1_result.method_result.elapsed / iteration1, method2: method2_result.method_result.elapsed / iteration2})
        scores = [
            ProblemResult.average_of_dicts(feasible_num),
            ProblemResult.average_of_dicts(elapsed),
            ProblemResult.average_of_dicts(statistics),
            ProblemResult.average_of_dicts(pvalues),
            ProblemResult.average_of_dicts(mean),
            ProblemResult.average_of_dicts(std),
            ProblemResult.average_of_dicts(max_num),
            ProblemResult.average_of_dicts(min_num)]
        return scores
    
    def statistical_list_analysis(self, methods: List[str], weights: Dict[str, float], alternative: str = "two-sided"):
        """
        p_value [summary] return statistical analysis of two solutions with two different methods indicated by
        [statistic: float, p_value: float, mean: float, std: float, max: float: min: float].

        alternative: str
        -------
        * 'two-sided': one of the distributions (underlying `x` or `y`) is
          stochastically greater than the other.
        * 'less': the distribution underlying `x` is stochastically less
          than the distribution underlying `y`.
        * 'greater': the distribution underlying `x` is stochastically greater
          than the distribution underlying `y`.
        """
        method_results = []
        iteration = 0
        for method in methods:
            assert method in self.methods_results
            method_result = self.methods_results[method].make_method_result(single_flag=True)
            method_results.append({method: method_result})
            iteration = max(iteration, self.methods_results[method].iteration)

        w = []
        for k, v in weights.items():
            w.append(v)
        # calculate
        feasible_num: List[Dict[str, float]] = []
        elapsed: List[Dict[str, float]] = []
        statistics: List[Dict[str, float]] = []
        pvalues: List[Dict[str, float]] = []
        mean: List[Dict[str, float]] = []
        std: List[Dict[str, float]] = []
        max_num: List[Dict[str, float]] = []
        min_num: List[Dict[str, float]] = []
        for i in range(iteration):
            methods_objective = {method: self.methods_results[method].results[i%self.methods_results[method].iteration].get_wso_objective(w) for method in methods}
            # N/A indicates ‘‘not applicable’’ which means that the corresponding
            # algorithm could not statistically compare with itself in the rank-sum test
            # N/A means itself for Wilcoxon’s ranksums p_value
            s: Dict[str, float] = {}
            p: Dict[str, float] = {}
            for i in range(len(methods)):
                statistic, pvalue = stats.ranksums(np.array(methods_objective[methods[-1]]), np.array(methods_objective[methods[i]]), alternative=alternative)
                s[methods[i]] = statistic
                p[methods[i]] = pvalue
            statistics.append(s)
            pvalues.append(p)
            feasible_num.append({method: self.methods_results[method].results[i%self.methods_results[method]].feasible_num for method in methods})
            mean.append({method: np.mean(methods_objective[method]) for method in methods})
            std.append({method: np.std(methods_objective[method]) for method in methods})
            max_num.append({method: np.max(methods_objective[method]) for method in methods})
            min_num.append({method: np.min(methods_objective[method]) for method in methods})
            elapsed.append({method: self.methods_results[method].method_result.elapsed for method in methods})
        scores = [
            ProblemResult.average_of_dicts(feasible_num),
            ProblemResult.average_of_dicts(elapsed),
            ProblemResult.average_of_dicts(statistics),
            ProblemResult.average_of_dicts(pvalues),
            ProblemResult.average_of_dicts(mean),
            ProblemResult.average_of_dicts(std),
            ProblemResult.average_of_dicts(max_num),
            ProblemResult.average_of_dicts(min_num)]
        return scores

    def average_compare(self, union_method: str, average_method: str) -> List[Dict[str, float]]:
        """union_average_compare [summary] return union method compared with average method with scores indicated by
        [elapsed time, found, front, igd, hv, spacing].
        """
        assert union_method in self.methods_results
        assert average_method in self.methods_results
        # prepare union result
        union_method_result = self.methods_results[union_method]
        # if union_method_result.method_result is None:
        #     union_method_result.make_method_result(single_flag=False)
        
        # prepare average results
        average_method_result = self.methods_results[average_method]
        # if average_method_result.method_result is None:
        #     average_method_result.make_method_result(single_flag=False)

        # compare
        elapsed: List[Dict[str, float]] = []
        found: List[Dict[str, float]] = []
        front_all: List[Dict[str, float]] = []
        igd_all: List[Dict[str, float]] = []
        hv_all: List[Dict[str, float]] = []
        sp_all: List[Dict[str, float]] = []
        tts_all: List[Dict[str, float]] = []
        iteration1 = union_method_result.iteration
        iteration2 = average_method_result.iteration
        iteration = max(iteration1, iteration2)
        for i in range(iteration):
            index1 = i % iteration1
            index2 = i % iteration2
            problem_archive = \
                ProblemArchive(self.problem, {union_method: union_method_result.results[index1],
                                              average_method: average_method_result.results[index2]})
            elapsed.append({union_method: union_method_result.results[index1].elapsed,
                            average_method: average_method_result.results[index2].elapsed})
            found.append({union_method: len(union_method_result.results[index1].solution_list),
                          average_method: len(average_method_result.results[index2].solution_list)})
            front_all.append({k: float(v) for k, v in problem_archive.on_pareto_count().items()})
            igd_all.append(problem_archive.compute_igd())
            hv_all.append(problem_archive.compute_hv())
            sp_all.append(problem_archive.compute_sp())
            # tts_all.append(problem_archive.compute_tts())
        # collect scores
        scores = [ProblemResult.average_of_dicts(elapsed),
                  ProblemResult.average_of_dicts(found),
                  ProblemResult.average_of_dicts(front_all),
                  ProblemResult.average_of_dicts(igd_all),
                  ProblemResult.average_of_dicts(hv_all),
                  ProblemResult.average_of_dicts(sp_all),
                #   ProblemResult.average_of_dicts(tts_all)
                  ]
        return scores
    
    def average_list_compare(self, methods: List[str]) -> List[Dict[str, float]]:
        """union_average_compare [summary] return union method compared with average method with scores indicated by
        [elapsed time, found, front, igd, hv, spacing].
        """
        # prepare result
        method_results = []
        iteration = 0
        for method in methods:
            assert method in self.methods_results
            method_result = self.methods_results[method].make_method_result(single_flag=False)
            method_results.append({method: method_result})
            iteration = max(iteration, self.methods_results[method].iteration)

        # compare
        elapsed: List[Dict[str, float]] = []
        found: List[Dict[str, float]] = []
        front_all: List[Dict[str, float]] = []
        igd_all: List[Dict[str, float]] = []
        hv_all: List[Dict[str, float]] = []
        sp_all: List[Dict[str, float]] = []
        tts_all: List[Dict[str, float]] = []

        for i in range(iteration):
            problem_archive = \
                ProblemArchive(self.problem, 
                               {method: self.methods_results[method].results[i % self.methods_results[method].iteration] \
                                 for method in methods})
            elapsed.append({method: self.methods_results[method].results[i % self.methods_results[method].iteration].elapsed \
                                 for method in methods})
            found.append({method: len(self.methods_results[method].results[i % self.methods_results[method].iteration].solution_list) \
                                 for method in methods})
            front_all.append({k: float(v) for k, v in problem_archive.on_pareto_count().items()})
            igd_all.append(problem_archive.compute_igd())
            hv_all.append(problem_archive.compute_hv())
            sp_all.append(problem_archive.compute_sp())
            tts_all.append(problem_archive.compute_tts())
        # collect scores
        scores = [ProblemResult.average_of_dicts(elapsed),
                  ProblemResult.average_of_dicts(found),
                  ProblemResult.average_of_dicts(front_all),
                  ProblemResult.average_of_dicts(igd_all),
                  ProblemResult.average_of_dicts(hv_all),
                  ProblemResult.average_of_dicts(sp_all),
                  ProblemResult.average_of_dicts(tts_all)
                  ]
        return scores

    def union_average_exact_compare(self, union_method: str, average_method: str, exact_method: str) -> List[Dict[str, float]]:
        """union_average_compare [summary] return union method compared with average method with scores indicated by
        [elapsed time, found, front, igd, hv, spacing].
        """
        assert union_method in self.methods_results
        assert average_method in self.methods_results
        # prepare union result
        union_method_result = self.methods_results[union_method]
        if union_method_result.method_result is None:
            union_method_result.make_method_result()
        iteration = union_method_result.iteration
        union_result = union_method_result.method_result
        union_elapsed = union_result.elapsed / iteration
        assert union_result is not None
        # prepare average results
        average_method_result = self.methods_results[average_method]
        iteration = average_method_result.iteration
        average_elapsed = sum(average_method_result.get_elapseds()) / iteration
        average_results = average_method_result.results
        # prepare exact results
        exact_method_result = self.methods_results[exact_method]
        if exact_method_result.method_result is None:
            exact_method_result.make_method_result()
        exact_result = exact_method_result.method_result
        assert exact_result is not None
        # compare
        elapsed = {union_method: union_elapsed, average_method: average_elapsed, exact_method: exact_result.elapsed}
        found = {union_method: len(union_result),
                 average_method: (sum([len(r) for r in average_results]) / iteration),
                 exact_method: len(exact_result)}
        front_all: List[Dict[str, float]] = []
        igd_all: List[Dict[str, float]] = []
        hv_all: List[Dict[str, float]] = []
        sp_all: List[Dict[str, float]] = []
        tts_all: List[Dict[str, float]] = []
        for i in range(iteration):
            average_result = average_results[i]
            problem_archive = \
                ProblemArchive(self.problem, {union_method: union_result, average_method: average_result, exact_method: exact_result})
            front_all.append({k: float(v) for k, v in problem_archive.on_pareto_count().items()})
            igd_all.append(problem_archive.compute_igd())
            hv_all.append(problem_archive.compute_hv())
            sp_all.append(problem_archive.compute_sp())
            tts_all.append(problem_archive.compute_tts())
        # collect scores
        scores = [elapsed, found, ProblemResult.average_of_dicts(front_all),
                  ProblemResult.average_of_dicts(igd_all),
                  ProblemResult.average_of_dicts(hv_all),
                  ProblemResult.average_of_dicts(sp_all),
                  ProblemResult.average_of_dicts(tts_all)
                  ]
        return scores

    def union_average_compare(self, union_method: str, average_method: str) -> List[Dict[str, float]]:
        """union_average_compare [summary] return union method compared with average method with scores indicated by
        [elapsed time, found, front, igd, hv, spacing].
        """
        assert union_method in self.methods_results
        assert average_method in self.methods_results
        # prepare union result
        union_method_result = self.methods_results[union_method]
        if union_method_result.method_result is None:
            union_method_result.make_method_result(single_flag=False)
        union_result = union_method_result.method_result
        assert union_result is not None
        # prepare average results
        average_method_result = self.methods_results[average_method]
        iteration = average_method_result.iteration
        average_elapsed = sum(average_method_result.get_elapseds()) / iteration
        average_results = average_method_result.results
        # compare
        elapsed = {union_method: union_result.elapsed, average_method: average_elapsed}
        found = {union_method: len(union_result),
                 average_method: (sum([len(r) for r in average_results]) / iteration)}
        front_all: List[Dict[str, float]] = []
        igd_all: List[Dict[str, float]] = []
        hv_all: List[Dict[str, float]] = []
        sp_all: List[Dict[str, float]] = []
        # tts_all: List[Dict[str, float]] = []
        for i in range(iteration):
            average_result = average_results[i]
            problem_archive = \
                ProblemArchive(self.problem, {union_method: union_result, average_method: average_result})
            front_all.append({k: float(v) for k, v in problem_archive.on_pareto_count().items()})
            igd_all.append(problem_archive.compute_igd())
            hv_all.append(problem_archive.compute_hv())
            sp_all.append(problem_archive.compute_sp())
            # tts_all.append(problem_archive.compute_tts())
        # collect scores
        scores = [elapsed, found, ProblemResult.average_of_dicts(front_all),
                  ProblemResult.average_of_dicts(igd_all),
                  ProblemResult.average_of_dicts(hv_all),
                  ProblemResult.average_of_dicts(sp_all),
                  # ProblemResult.average_of_dicts(tts_all)
                  ]
        return scores

    @staticmethod
    def result_compare(problem: Problem, method_results: Dict[str, Result]) -> List[Dict[str, float]]:
        """result_compare [summary] compare archives, return scores are ordered as:
            front, igd, hv, spacing.
        """
        problem_archive = ProblemArchive(problem, method_results)
        # calculate or count the scores
        front = {k: float(v) for k, v in problem_archive.on_pareto_count().items()}
        igd = problem_archive.compute_igd()
        hv = problem_archive.compute_hv()
        sp = problem_archive.compute_sp()
        return [front, igd, hv, sp]
