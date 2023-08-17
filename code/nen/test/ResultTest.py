import unittest
from typing import List
import random
from os import path
from pathlib import Path
from datetime import datetime
from jmetal.core.solution import BinarySolution
from nen.Result import NDArchive, MethodResult, Result, HashableObjectives, ProblemArchive, ProblemResult
from nen.Problem import Problem
from nen.util.util import FLOAT_PRECISION, RESULT_ROOT


class ResultTest(unittest.TestCase):
    LOOP_TIMES = 100
    RANDOM_LIST_LENGTH = 50
    ARCHIVES_NUM = 20
    SOLUTIONS_PER_ARCHIVE = 200

    def reset_seed(self) -> None:
        random.seed(datetime.now())

    def test_str_list_convertion(self) -> None:
        self.reset_seed()
        for _ in range(ResultTest.LOOP_TIMES):
            # bool list string convertion
            bool_list = [True if random.randint(0, 1) == 1 else False for _ in range(ResultTest.RANDOM_LIST_LENGTH)]
            reconsitituted_b = NDArchive.str_to_bool_list(NDArchive.bool_list_to_str(bool_list))
            assert len(bool_list) == len(reconsitituted_b)
            for i in range(ResultTest.RANDOM_LIST_LENGTH):
                assert bool_list[i] == reconsitituted_b[i]
            # float list string convertion
            float_list = [random.random() for _ in range(ResultTest.RANDOM_LIST_LENGTH)]
            reconsitituted_f = NDArchive.str_to_float_list(NDArchive.float_list_to_str(float_list))
            assert len(float_list) == len(reconsitituted_f)
            for i in range(ResultTest.RANDOM_LIST_LENGTH):
                assert round(float_list[i], NDArchive.ROUND_PRECISION) == \
                    round(reconsitituted_f[i], NDArchive.ROUND_PRECISION)

    def test_add_to_archive(self) -> None:
        # create an empty problem
        problem = Problem()
        problem.variables = ['x', 'y', 'z']
        problem.objectives = {'#1': {'x': 1, 'z': 1}, '#2': {'y': 1}}
        problem.constraints = []
        problem.variables_num = 3
        problem.objectives_num = 2
        problem.constraints_num = 0
        problem.variables_index = {'x': 0, 'y': 1, 'z': 2}
        problem.objectives_order = ['#1', '#2']
        problem.objectives_index = {'#1': 0, '#2': 1}
        # add into archive
        arxv = NDArchive(problem.variables_num, problem.objectives_num)
        # (1, 1)
        arxv.add(problem.evaluate({'x': True, 'y': True, 'z': False}))
        # (1, 1)
        arxv.add(problem.evaluate({'x': True, 'y': True, 'z': False}))
        assert len(arxv) == 1
        # (2, 1)
        arxv.add(problem.evaluate({'x': True, 'y': True, 'z': True}))
        assert len(arxv) == 1
        # (0, 1)
        arxv.add(problem.evaluate({'x': False, 'y': True, 'z': False}))
        # (1, 1)
        arxv.add(problem.evaluate({'x': True, 'y': True, 'z': False}))
        assert len(arxv) == 1
        # (1, 0)
        arxv.add(problem.evaluate({'x': True, 'y': False, 'z': False}))
        assert len(arxv) == 2
        # (0, 0)
        arxv.add(problem.evaluate({'x': False, 'y': False, 'z': False}))
        assert len(arxv) == 1

    def test_dominate(self) -> None:
        s1 = BinarySolution(0, 2, 0)
        s1.objectives = [3.33, 2.22]
        s2 = BinarySolution(0, 2, 0)
        s2.objectives = [3.33, 3.22]
        assert NDArchive.dominate(s1, s2) and not NDArchive.dominate(s2, s1)
        s2.objectives = [3.34, 2.21]
        assert not NDArchive.dominate(s1, s2) and not NDArchive.dominate(s2, s1)
        s2.objectives = [3.33, 2.22]
        assert not NDArchive.dominate(s1, s2) and not NDArchive.dominate(s2, s1)
        s2.objectives = [3.22, 2.11]
        assert not NDArchive.dominate(s1, s2) and NDArchive.dominate(s2, s1)

    def same_float_list(self, l1: List[float], l2: List[float]) -> bool:
        if len(l1) != len(l2): return False
        for index in range(len(l1)):
            if abs(l1[index] - l2[index]) >= FLOAT_PRECISION: return False
        return True

    def test_method_result_dump(self) -> None:
        problem = Problem()
        problem.variables = ['x', 'y', 'z']
        problem.objectives = {'#1': {}, '#2': {}}
        problem.constraints = []
        problem.variables_num = 3
        problem.objectives_num = 2
        problem.constraints_num = 0
        problem.variables_index = {'x': 0, 'y': 1, 'z': 2}
        problem.objectives_order = ['#1', '#2']
        problem.objectives_index = {'#1': 0, '#2': 1}
        parent_path = path.join(RESULT_ROOT, 'testProblem')
        Path(parent_path).mkdir(parents=False, exist_ok=True)
        sr_ = MethodResult('method1', parent_path, problem)
        s1 = BinarySolution(3, 2, 1)
        s1.variables = [[True, False, False]]
        s1.objectives = [3.33, 2.22]
        s2 = BinarySolution(3, 2, 1)
        s2.variables = [[True, False, True]]
        s2.objectives = [3.23, 2.22]
        s3 = BinarySolution(3, 2, 1)
        s3.variables = [[False, True, True]]
        s3.objectives = [2.00, 3.33]
        s4 = BinarySolution(3, 2, 1)
        s4.variables = [[False, True, False]]
        s4.objectives = [1.09, 4.37]
        s5 = BinarySolution(3, 2, 1)
        s5.variables = [[True, True, True]]
        s5.objectives = [2.00, 3.00]
        s6 = BinarySolution(3, 2, 1)
        s6.variables = [[True, True, True]]
        s6.objectives = [4.99, 0.21]
        arxv = Result(problem)
        arxv.add(s1)
        arxv.add(s2)
        arxv.add(s3)
        arxv.add(s4)
        arxv.add(s5)
        arxv.add(s6)
        assert len(arxv) == 4
        arxv.elapsed = 3.14
        paretos = [s4, s5, s2, s6]
        sr_.add(arxv)
        Path(sr_.path).mkdir(parents=True, exist_ok=True)
        sr_.dump_result(0)
        sr = MethodResult('method1', parent_path, problem)
        sr.load_result(0, False)
        solutions = sr.get_solution_list(0)
        assert len(solutions) == len(paretos), [x.objectives for x in solutions]
        for i in range(len(paretos)):
            assert solutions[i].variables == paretos[i].variables
            assert self.same_float_list(solutions[i].objectives, paretos[i].objectives)
        sr_.dump_info()
        sr.load_info()
        assert sr_.info == sr.info

        sr2_ = MethodResult('method2', parent_path, problem)
        arxv2 = Result(problem)
        arxv2.add(s1)
        arxv2.add(s2)
        arxv2.add(s3)
        arxv2.add(s4)
        arxv2.add(s5)
        arxv2.add(s6)
        arxv2.elapsed = 3.14
        sr2_.add(arxv2)
        sr2 = MethodResult('method2', parent_path, problem)
        sr2_.dump()
        sr2.load(False)
        s2_ = sr2_.get_solution_list(0)
        s2 = sr2.get_solution_list(0)
        assert len(s2_) == len(s2)
        for i in range(len(s2_)):
            assert s2_[i].variables == s2[i].variables
            assert self.same_float_list(s2_[i].objectives, s2[i].objectives)

    def same_method_result(self, r1: MethodResult, r2: MethodResult) -> bool:
        if r1.name != r2.name: return False
        if r1.parent_path != r2.parent_path: return False
        if r1.path != r2.path: return False
        if r1.info != r2.info: return False
        if len(r1.results) != len(r2.results): return False
        for index in range(r1.iteration):
            s1, s2 = r1.get_solution_list(index), r2.get_solution_list(index)
            assert len(s1) == len(s2), (index, len(s1), len(s2))
            for i in range(len(s1)):
                if s1[i].variables != s2[i].variables: return False
                if not self.same_float_list(s1[i].objectives, s2[i].objectives): return False
        return True

    def random_variables(self) -> List[bool]:
        return [random.randint(0, 1) == 1 for _ in range(ResultTest.RANDOM_LIST_LENGTH)]

    def _random_archive(self) -> NDArchive:
        random.seed(datetime.now())
        solution_list: List[BinarySolution] = []
        for _ in range(ResultTest.SOLUTIONS_PER_ARCHIVE):
            solution = BinarySolution(ResultTest.RANDOM_LIST_LENGTH, 2)
            solution.variables = [self.random_variables()]
            solution.objectives = [round(random.random() * 100, NDArchive.ROUND_PRECISION),
                                   round(random.random() * 100, NDArchive.ROUND_PRECISION)]
            solution_list.append(solution)
        arx = NDArchive(ResultTest.RANDOM_LIST_LENGTH, 2)
        arx.set_solution_list(solution_list)
        return arx

    def random_result(self, problem: Problem) -> Result:
        random.seed(datetime.now())
        result = Result(problem)
        result.elapsed = random.random()
        # random solution list
        for _ in range(ResultTest.SOLUTIONS_PER_ARCHIVE):
            solution = BinarySolution(ResultTest.RANDOM_LIST_LENGTH, 2)
            solution.variables = [self.random_variables()]
            solution.objectives = [round(random.random() * 100, NDArchive.ROUND_PRECISION),
                                   round(random.random() * 100, NDArchive.ROUND_PRECISION)]
            result.add(solution)
        return result

    def test_method_result_with_many_iteration_dump(self) -> None:
        problem = Problem()
        problem.variables = ['x{}'.format(i) for i in range(ResultTest.RANDOM_LIST_LENGTH)]
        problem.objectives = {'#1': {}, '#2': {}}
        problem.constraints = []
        problem.variables_num = ResultTest.RANDOM_LIST_LENGTH
        problem.objectives_num = 2
        problem.constraints_num = 0
        problem.variables_index = {'x{}'.format(i): i for i in range(ResultTest.RANDOM_LIST_LENGTH)}
        problem.objectives_order = ['#1', '#2']
        problem.objectives_index = {'#1': 0, '#2': 1}
        parent_path = path.join(RESULT_ROOT, 'testProblem')
        Path(parent_path).mkdir(parents=False, exist_ok=True)
        for _ in range(ResultTest.LOOP_TIMES):
            sr_ = MethodResult('method3', parent_path, problem)
            for _ in range(ResultTest.ARCHIVES_NUM):
                sr_.add(self.random_result(problem))
            sr_.info['lyrics'] = 'alle menschen werden brüder wo dein sanfter flügel weilt'
            sr_.dump()
            sr = MethodResult('method3', parent_path, problem)
            sr.load(False)
            assert self.same_method_result(sr_, sr)

    def test_method_archive(self) -> None:
        problem = Problem()
        problem.variables = []
        problem.objectives = {'#1': {}, '#2': {}}
        problem.constraints = []
        problem.variables_num = 0
        problem.objectives_num = 2
        problem.constraints_num = 0
        problem.variables_index = {}
        problem.objectives_order = ['#1', '#2']
        problem.objectives_index = {'#1': 0, '#2': 1}
        parent_path = path.join(RESULT_ROOT, 'testProblem')
        Path(parent_path).mkdir(parents=False, exist_ok=True)
        sr = MethodResult('method1', parent_path, problem)
        s1 = BinarySolution(0, 2, 0)
        s2 = BinarySolution(0, 2, 0)
        s3 = BinarySolution(0, 2, 0)
        s4 = BinarySolution(0, 2, 0)
        s5 = BinarySolution(0, 2, 0)
        s6 = BinarySolution(0, 2, 0)
        s7 = BinarySolution(0, 2, 0)
        s8 = BinarySolution(0, 2, 0)
        s9 = BinarySolution(0, 2, 0)
        s1.variables = [[]]
        s2.variables = [[]]
        s3.variables = [[]]
        s4.variables = [[]]
        s5.variables = [[]]
        s6.variables = [[]]
        s7.variables = [[]]
        s8.variables = [[]]
        s9.variables = [[]]
        s1.objectives = [10, 1]
        s2.objectives = [8, 1]
        s3.objectives = [9, 1]
        s4.objectives = [7, 3]
        s5.objectives = [5, 5]
        s6.objectives = [5, 6]
        s7.objectives = [5, 4]
        s8.objectives = [3, 10]
        s9.objectives = [1, 9]
        a1 = Result(problem)
        a1.add(s1)
        a1.add(s4)
        a1.add(s5)
        a1.add(s8)
        a2 = Result(problem)
        a2.add(s1)
        a2.add(s2)
        a2.add(s6)
        a2.add(s8)
        a3 = Result(problem)
        a3.add(s1)
        a3.add(s4)
        a3.add(s7)
        a3.add(s9)

        sr.add(a1)
        sr.add(a2)
        sr.add(a3)
        sr.make_method_result()
        method_result = sr.get_method_result()
        assert method_result is not None
        assert len(method_result) == 4


class ProblemResultTest(unittest.TestCase):
    # configs
    OBECTIVES_NUM = 3
    ARCHIVE_SIZE = 1000
    FLOAT_PRECISION = 1e-6

    VAR_NUM = 100
    ITERATION = 10
    METHOD_NUM = 3

    LOOP_TIMES = 10

    def test_hashable_objectives(self) -> None:
        s1 = BinarySolution(0, 2, 0)
        s2 = BinarySolution(0, 2, 0)
        s3 = BinarySolution(0, 2, 0)
        s4 = BinarySolution(0, 2, 0)
        s5 = BinarySolution(0, 2, 0)
        s1.objectives = [3.22, 2.33]
        s2.objectives = [1.22, 3.33]
        s3.objectives = [5.22, 4.33]
        s4.objectives = [2.22, 2.33]
        objectives_set = set()
        objectives_set.add(HashableObjectives(s1))
        objectives_set.add(HashableObjectives(s1))
        objectives_set.add(HashableObjectives(s1))
        objectives_set.add(HashableObjectives(s2))
        objectives_set.add(HashableObjectives(s3))
        objectives_set.add(HashableObjectives(s1))
        objectives_set.add(HashableObjectives(s4))
        objectives_set.add(HashableObjectives(s2))
        assert len(objectives_set) == 4, len(objectives_set)
        assert HashableObjectives(s1) in objectives_set
        assert HashableObjectives(s2) in objectives_set
        assert HashableObjectives(s3) in objectives_set
        assert HashableObjectives(s4) in objectives_set
        s5.objectives = [4.22, 8.33]
        assert HashableObjectives(s5) not in objectives_set

    def test_problem_archive(self) -> None:
        p = Problem()
        p.variables_num = 0
        p.objectives_num = 2

        r1 = MethodResult('m1', '', p)
        r2 = MethodResult('m2', '', p)

        s1_list = [[1, 5.4], [1, 3], [2, 3], [2, 2], [3, 4], [3, 1], [4, 0]]
        s2_list = [[1, 2.5], [3, 1.5], [4, 0], [5, 2]]

        r1_result = Result(p)
        for obj in s1_list:
            solution = BinarySolution(0, 2, 1)
            solution.variables = [[]]
            solution.objectives = obj
            r1_result.add(solution)
        r1.add(r1_result)
        r1.make_method_result()

        r2_result = Result(p)
        for obj in s2_list:
            solution = BinarySolution(0, 2, 1)
            solution.variables = [[]]
            solution.objectives = obj
            r2_result.add(solution)
        r2.add(r2_result)
        r2.make_method_result()

        mr1 = r1.method_result
        mr2 = r2.method_result
        assert mr1 is not None and len(mr1) == 4
        assert mr2 is not None and len(mr2) == 3

        pa = ProblemArchive(p, {'m1': mr1, 'm2': mr2})
        assert len(pa.archive) == 4
        front = pa.on_pareto_count()
        assert front == {'m1': 3, 'm2': 2}
        found = pa.solutions_count()
        assert found == {'m1': 4, 'm2': 3}
        rp = pa.reference_point()
        assert rp == [5.0, 3.5], rp

    def random_objectives_solution(self) -> BinarySolution:
        solution = BinarySolution(0, ProblemResultTest.OBECTIVES_NUM, 0)
        solution.objectives = [random.random() for _ in range(ProblemResultTest.OBECTIVES_NUM)]
        return solution

    def test_archive_to_array(self) -> None:
        random.seed(datetime.now())
        archive = NDArchive(0, ProblemResultTest.OBECTIVES_NUM)
        for _ in range(ProblemResultTest.ARCHIVE_SIZE):
            archive.archive.solution_list.append(self.random_objectives_solution())
        array = ProblemArchive.archive_to_array(archive)
        assert len(array) == len(archive)
        for i in range(ProblemResultTest.ARCHIVE_SIZE):
            for j in range(ProblemResultTest.OBECTIVES_NUM):
                assert abs(array[i, j] - archive.solution_list[i].objectives[j]) < ProblemResultTest.FLOAT_PRECISION

    def test_if_could_run_indicaters(self) -> None:
        p = Problem()
        p.variables_num = 0
        p.objectives_num = 2
        r1 = MethodResult('m1', '', p)
        r2 = MethodResult('m2', '', p)
        r1_result = Result(p)
        r2_result = Result(p)
        for obj in [[1, 5.4], [1, 3], [2, 3], [2, 2], [3, 4], [3, 1], [4, 0]]:
            solution = BinarySolution(0, 2, 1)
            solution.variables = [[]]
            solution.objectives = obj
            r1_result.add(solution)
        for obj in [[1, 2.5], [3, 1.5], [4, 0], [5, 2]]:
            solution = BinarySolution(0, 2, 1)
            solution.variables = [[]]
            solution.objectives = obj
            r2_result.add(solution)
        r1.add(r1_result)
        r2.add(r2_result)
        r1.make_method_result()
        r2.make_method_result()
        mr1 = r1.method_result
        mr2 = r2.method_result
        assert mr1 is not None and mr2 is not None
        pa = ProblemArchive(p, {'m1': mr1, 'm2': mr2})
        scores_list = pa.compute(['igd', 'hv', 'sp'])
        assert len(scores_list) == 3
        for scores in scores_list:
            assert len(scores) == 2
            assert 'm1' in scores
            assert 'm2' in scores

    def random_variables(self) -> List[bool]:
        return [random.randint(0, 1) == 1 for _ in range(ProblemResultTest.VAR_NUM)]

    def _random_archive(self) -> NDArchive:
        random.seed(datetime.now())
        solution_list: List[BinarySolution] = []
        for _ in range(ProblemResultTest.ARCHIVE_SIZE):
            solution = BinarySolution(ProblemResultTest.VAR_NUM, ProblemResultTest.OBECTIVES_NUM)
            solution.variables = [self.random_variables()]
            solution.objectives = [round(random.random() * 100, NDArchive.ROUND_PRECISION)
                                   for _ in range(ProblemResultTest.OBECTIVES_NUM)]
            solution_list.append(solution)
        arx = NDArchive(ProblemResultTest.VAR_NUM, ProblemResultTest.OBECTIVES_NUM)
        arx.set_solution_list(solution_list)
        return arx

    def random_result(self, problem: Problem) -> Result:
        random.seed(datetime.now())
        result = Result(problem)
        for _ in range(ProblemResultTest.ARCHIVE_SIZE):
            solution = BinarySolution(ProblemResultTest.VAR_NUM, ProblemResultTest.OBECTIVES_NUM)
            solution.variables = [self.random_variables()]
            solution.objectives = [round(random.random() * 100, NDArchive.ROUND_PRECISION)
                                   for _ in range(ProblemResultTest.OBECTIVES_NUM)]
            result.add(solution)
        result.elapsed = random.random()
        return result

    def random_method_result(self, name: str, path: str, problem: Problem) -> MethodResult:
        mr = MethodResult(name, path, problem)
        for _ in range(ProblemResultTest.ITERATION):
            mr.add(self.random_result(problem))
        return mr

    def same_float_list(self, l1: List[float], l2: List[float]) -> bool:
        if len(l1) != len(l2): return False
        for index in range(len(l1)):
            if abs(l1[index] - l2[index]) >= FLOAT_PRECISION: return False
        return True

    def same_method_result(self, r1: MethodResult, r2: MethodResult) -> bool:
        if r1.name != r2.name: return False
        if r1.parent_path != r2.parent_path: return False
        if r1.path != r2.path: return False
        if r1.info != r2.info: return False
        if len(r1.results) != len(r1.results): return False
        for index in range(r1.info['iteration']):
            s1, s2 = r1.get_solution_list(index), r2.get_solution_list(index)
            assert len(s1) == len(s2), (len(s1), len(s2))
            for i in range(len(s1)):
                if s1[i].variables != s2[i].variables: return False
                if not self.same_float_list(s1[i].objectives, s2[i].objectives): return False
        return True

    def test_problem_result_dump(self) -> None:
        for _ in range(ProblemResultTest.LOOP_TIMES):
            # random problem result
            problem = Problem()
            problem.variables_num = ProblemResultTest.VAR_NUM
            problem.objectives_num = ProblemResultTest.OBECTIVES_NUM
            pr_ = ProblemResult('testProblem', problem)
            for i in range(ProblemResultTest.METHOD_NUM):
                pr_.add(self.random_method_result('m{}'.format(i), pr_.path, problem))
            pr_.dump()
            pr = ProblemResult('testProblem', problem)
            pr.load(['m{}'.format(i) for i in range(ProblemResultTest.METHOD_NUM)], False)
            for method in ['m{}'.format(i) for i in range(ProblemResultTest.METHOD_NUM)]:
                assert method in pr.methods_results
                assert self.same_method_result(pr.methods_results[method], pr_.methods_results[method])
