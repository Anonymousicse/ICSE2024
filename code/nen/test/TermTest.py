import unittest
from typing import Dict, List, Tuple, Any
import random
from copy import deepcopy
from datetime import datetime
from nen.Term import Linear, Quadratic, Constraint


class TermTest(unittest.TestCase):
    LOOP_TIMES = 30
    VARS_NUM = 10
    UNIFORM_LOWER = -99
    UNIFORM_UPPER = 99

    def reset_seed(self) -> None:
        random.seed(datetime.now())

    def random_linear_poly(self, size: int) -> Dict[str, float]:
        return {'x{}'.format(k): random.randint(TermTest.UNIFORM_LOWER, TermTest.UNIFORM_UPPER) for k in range(size)}

    def random_quadratic_poly(self, size: int) -> Dict[Tuple[str, str], float]:
        result: Dict[Tuple[str, str], float] = {}
        for i in range(size):
            for j in range(i + 1, size):
                result[('x{}'.format(i), 'x{}'.format(j))] = \
                    random.randint(TermTest.UNIFORM_LOWER, TermTest.UNIFORM_UPPER)
        return result

    def subfeature_list(self, size: int) -> List[str]:
        return ['y{}'.format(i) for i in range(size)]

    def unpack_denepndency(self, coef: Dict[str, float]) -> Tuple[str, str]:
        assert len(coef) == 2
        left, right = None, None
        for k, v in coef.items():
            if v == 1:
                left = k
            elif v == -1:
                right = k
        assert left is not None
        assert right is not None
        return (left, right)

    def test_constraint_self_check(self) -> None:
        Constraint()
        Constraint({'x': 1, 'y': 5}, '=', 100)
        Constraint({'x': 1, 'y': 0}, '<=', 3)
        Constraint('x', '=>', 'y')
        Constraint('x', '<=>', 'y')
        Constraint('x', '><', 'y')
        Constraint(['x', 'y', 'z'], 'or', 'f')
        Constraint(['xsdasdsdasdad', 'yzxczxczxc', 'zvccvc'], 'alt', 'f')

    def test_linear_and_quadratic(self) -> None:
        self.reset_seed()
        for _ in range(TermTest.LOOP_TIMES):
            coef = self.random_linear_poly(TermTest.VARS_NUM)
            sense = '='
            rhs = random.randint(TermTest.UNIFORM_LOWER, TermTest.UNIFORM_UPPER)
            lin = Linear(deepcopy(coef), deepcopy(sense), rhs)
            assert lin.coef == coef
            assert lin.sense == sense
            assert lin.rhs == rhs
        for _ in range(TermTest.LOOP_TIMES):
            quadratic = self.random_quadratic_poly(TermTest.VARS_NUM)
            linear = self.random_linear_poly(TermTest.VARS_NUM)
            constant = random.randint(TermTest.UNIFORM_LOWER, TermTest.UNIFORM_UPPER)
            kuadratik = Quadratic(deepcopy(quadratic), deepcopy(linear), constant)
            assert kuadratik.quadratic == quadratic
            assert kuadratik.linear == linear
            assert kuadratik.constant == constant

    def test_constraint_to_linear(self) -> None:
        self.reset_seed()
        # linear equation
        for _ in range(TermTest.LOOP_TIMES):
            coef = self.random_linear_poly(TermTest.VARS_NUM)
            rhs = random.randint(TermTest.UNIFORM_LOWER, TermTest.UNIFORM_UPPER)
            cst = Constraint(coef, '=', rhs)
            results = cst.to_linear()
            assert len(results) == 1
            result = results[0]
            assert isinstance(result, Linear)
            assert result.coef == coef
            assert result.sense == '='
            assert result.rhs == rhs
        # linear inequation
        for _ in range(TermTest.LOOP_TIMES):
            coef = self.random_linear_poly(TermTest.VARS_NUM)
            rhs = random.randint(TermTest.UNIFORM_LOWER, TermTest.UNIFORM_UPPER)
            cst = Constraint(coef, '<=', rhs)
            results = cst.to_linear()
            assert len(results) == 1
            result = results[0]
            assert isinstance(result, Linear)
            assert result.coef == coef
            assert result.sense == '<='
            assert result.rhs == rhs
        # mandatory
        for _ in range(TermTest.LOOP_TIMES):
            left = 'x{}'.format(random.randint(0, TermTest.VARS_NUM - 1))
            right = 'x{}'.format(random.randint(0, TermTest.VARS_NUM - 1))
            while left == right: right = 'x{}'.format(random.randint(0, TermTest.VARS_NUM - 1))
            cst = Constraint(left, '<=>', right)
            results = cst.to_linear()
            assert len(results) == 1
            result = results[0]
            assert isinstance(result, Linear)
            assert len(result.coef) == 2, result.coef
            assert left in result.coef and result.coef[left] == 1
            assert right in result.coef and result.coef[right] == -1
            assert result.sense == '='
            assert result.rhs == 0
        # dependency
        for _ in range(TermTest.LOOP_TIMES):
            left = 'x{}'.format(random.randint(0, TermTest.VARS_NUM - 1))
            right = 'x{}'.format(random.randint(0, TermTest.VARS_NUM - 1))
            while left == right: right = 'x{}'.format(random.randint(0, TermTest.VARS_NUM - 1))
            cst = Constraint(left, '=>', right)
            results = cst.to_linear()
            assert len(results) == 1
            result = results[0]
            assert isinstance(result, Linear)
            assert len(result.coef) == 2
            assert left in result.coef and result.coef[left] == 1
            assert right in result.coef and result.coef[right] == -1
            assert result.sense == '<='
            assert result.rhs == 0
        # exclude
        for _ in range(TermTest.LOOP_TIMES):
            left = 'x{}'.format(random.randint(0, TermTest.VARS_NUM - 1))
            right = 'x{}'.format(random.randint(0, TermTest.VARS_NUM - 1))
            while left == right: right = 'x{}'.format(random.randint(0, TermTest.VARS_NUM - 1))
            cst = Constraint(left, '><', right)
            results = cst.to_linear()
            assert len(results) == 1
            result = results[0]
            assert isinstance(result, Linear)
            assert len(result.coef) == 2
            assert left in result.coef and result.coef[left] == 1
            assert right in result.coef and result.coef[right] == 1
            assert result.sense == '<='
            assert result.rhs == 1
        # or subfeature, NOTE: this use assumption that sum is the last constraint
        for _ in range(TermTest.LOOP_TIMES):
            subfeatures = self.subfeature_list(TermTest.VARS_NUM)
            right_feature = 'x'
            cst = Constraint(subfeatures, 'or', right_feature)
            results = cst.to_linear()
            assert len(results) == len(subfeatures) + 1
            for result in results: assert isinstance(result, Linear)
            var_meet = set()
            for index in range(TermTest.VARS_NUM):
                linear_cst = results[index]
                left, right = self.unpack_denepndency(linear_cst.coef)
                assert left not in var_meet
                var_meet.add(left)
                assert right == right_feature
                assert linear_cst.sense == '<='
                assert linear_cst.rhs == 0
            last = results[-1]
            for index in range(TermTest.VARS_NUM):
                subfeature = 'y{}'.format(index)
                assert subfeature in last.coef
                assert last.coef[subfeature] == -1
            assert last.coef[right_feature] == 1
            assert last.sense == '<='
            assert last.rhs == 0
        # alt subfeatures, NOTE: this use assumption that sum is the last two constraint
        for _ in range(TermTest.LOOP_TIMES):
            subfeatures = self.subfeature_list(TermTest.VARS_NUM)
            right_feature = 'x'
            cst = Constraint(subfeatures, 'alt', right_feature)
            results = cst.to_linear()
            assert len(results) == len(subfeatures) + 2
            for result in results: assert isinstance(result, Linear)
            var_meet = set()
            for index in range(TermTest.VARS_NUM):
                linear_cst = results[index]
                left, right = self.unpack_denepndency(linear_cst.coef)
                assert left not in var_meet
                var_meet.add(left)
                assert right == right_feature
                assert linear_cst.sense == '<='
                assert linear_cst.rhs == 0
            last_two = results[-2]
            for index in range(TermTest.VARS_NUM):
                subfeature = 'y{}'.format(index)
                assert subfeature in last_two.coef and last_two.coef[subfeature] == 1
            assert last_two.coef[right_feature] == -1
            assert last_two.sense == '<='
            assert last_two.rhs == 0
            last_one = results[-1]
            for index in range(TermTest.VARS_NUM):
                subfeature = 'y{}'.format(index)
                assert subfeature in last_one.coef and last_one.coef[subfeature] == 1
            assert last_one.sense == '<='
            assert last_one.rhs == 1

    def pair_dict_equal(self, d1: Dict[Tuple[str, str], Any], d2: Dict[Tuple[str, str], Any]) -> bool:
        if len(d1) != len(d2): return False
        for (k1, k2), v in d1.items():
            if (k1, k2) in d2:
                if d2[(k1, k2)] != v: return False
            elif (k2, k1) in d2:
                if d2[(k2, k1)] != v: return False
            else:
                return False
        return True

    def test_constraint_to_quadratic_with_testcases(self) -> None:
        self.reset_seed()
        arts: List[str]
        # linear equation
        arts = []
        cst = Constraint({'x0': 1, 'x1': -3, 'x2': 5, 'x3': -7, 'x4': 9}, '=', 2)
        qdr = cst.to_quadratic(arts)
        assert len(arts) == 0
        assert qdr.constant == 4
        assert qdr.linear == {'x0': -3, 'x1': 21, 'x2': 5, 'x3': 77, 'x4': 45}, qdr.linear
        assert self.pair_dict_equal(qdr.quadratic, {
            ('x0', 'x1'): -6, ('x0', 'x2'): 10, ('x0', 'x3'): -14, ('x0', 'x4'): 18,
            ('x1', 'x2'): -30, ('x1', 'x3'): 42, ('x1', 'x4'): -54,
            ('x2', 'x3'): -70, ('x2', 'x4'): 90, ('x3', 'x4'): -126
        }), qdr.quadratic
        # linear inequation
        arts = []
        cst = Constraint({'x0': 1, 'x1': -2, 'x2': 3}, '<=', 2)
        qdr = cst.to_quadratic(arts)
        assert len(arts) == 3, arts
        assert qdr.constant == 4, (arts, qdr.linear, qdr.quadratic, qdr.constant)
        assert qdr.linear == {'$0': -3, '$1': -4, '$2': -3, 'x0': -3, 'x1': 12, 'x2': -3}
        assert self.pair_dict_equal(qdr.quadratic, {
            ('$0', '$1'): 4, ('$0', '$2'): 2, ('$0', 'x0'): 2, ('$0', 'x1'): -4, ('$0', 'x2'): 6,
            ('$1', '$2'): 4, ('$1', 'x0'): 4, ('$1', 'x1'): -8, ('$1', 'x2'): 12,
            ('$2', 'x0'): 2, ('$2', 'x1'): -4, ('$2', 'x2'): 6,
            ('x0', 'x1'): -4, ('x0', 'x2'): 6, ('x1', 'x2'): -12
        }), qdr.quadratic
        # denpendency
        arts = []
        cst = Constraint('x', '=>', 'y')
        qdr = cst.to_quadratic(arts)
        assert len(arts) == 0
        assert qdr.constant == 0
        assert qdr.linear == {'x': 1}
        assert self.pair_dict_equal(qdr.quadratic, {('x', 'y'): -1})
        # mandatory
        arts = []
        cst = Constraint('x', '<=>', 'y')
        qdr = cst.to_quadratic(arts)
        assert len(arts) == 0
        assert qdr.constant == 0
        assert qdr.linear == {'x': 1, 'y': 1}
        assert self.pair_dict_equal(qdr.quadratic, {('x', 'y'): -2})
        # exclude
        arts = []
        cst = Constraint('x', '><', 'y')
        qdr = cst.to_quadratic(arts)
        assert len(arts) == 0
        assert qdr.constant == 0
        assert len(qdr.linear) == 0
        assert self.pair_dict_equal(qdr.quadratic, {('x', 'y'): 1})
        # or subfeature
        arts = []
        cst = Constraint(['x', 'y', 'z'], 'or', 'f')
        qdr = cst.to_quadratic(arts)
        assert len(arts) == 2
        assert qdr.constant == 0
        assert qdr.linear == {'f': 1, '$0': 1, '$1': 4, 'x': 2, 'y': 2, 'z': 2}
        assert self.pair_dict_equal(qdr.quadratic, {
            ('f', '$0'): 2, ('f', '$1'): 4, ('f', 'x'): -3, ('f', 'y'): -3, ('f', 'z'): -3,
            ('$0', '$1'): 4, ('$0', 'x'): -2, ('$0', 'y'): -2, ('$0', 'z'): -2,
            ('$1', 'x'): -4, ('$1', 'y'): -4, ('$1', 'z'): -4,
            ('x', 'y'): 2, ('x', 'z'): 2, ('y', 'z'): 2
        })
        # alt subfeature
        arts = []
        cst = Constraint(['x', 'y', 'z'], 'alt', 'f')
        qdr = cst.to_quadratic(arts)
        assert len(arts) == 3, (arts, qdr.linear, qdr.quadratic, qdr.constant)
        assert qdr.constant == 1
        assert qdr.linear == {'f': 1, '$0': 1, '$1': 4, '$2': -1, 'x': 1, 'y': 1, 'z': 1}
        assert self.pair_dict_equal(qdr.quadratic, {
            ('f', '$0'): 2, ('f', '$1'): 4, ('f', 'x'): -3, ('f', 'y'): -3, ('f', 'z'): -3,
            ('$0', '$1'): 4, ('$0', 'x'): -2, ('$0', 'y'): -2, ('$0', 'z'): -2,
            ('$1', 'x'): -4, ('$1', 'y'): -4, ('$1', 'z'): -4,
            ('$2', 'x'): 2, ('$2', 'y'): 2, ('$2', 'z'): 2,
            ('x', 'y'): 4, ('x', 'z'): 4, ('y', 'z'): 4
        })

    def test_evaluate(self) -> None:
        # linear equation
        cst = Constraint({'x': 1, 'y': 2, 'z': 1}, '=', 2)
        assert not cst.evaluate({'x': True, 'y': True, 'z': True})
        assert not cst.evaluate({'x': True, 'y': True, 'z': False})
        assert not cst.evaluate({'x': False, 'y': False, 'z': False})
        assert cst.evaluate({'x': True, 'y': False, 'z': True})
        assert cst.evaluate({'x': False, 'y': True, 'z': False})
        # cst = Constraint({'x': 1.0000000000001, 'y': 2, 'z': 1}, '=', 2)
        assert cst.evaluate({'x': True, 'y': False, 'z': True})
        assert cst.evaluate({'x': False, 'y': True, 'z': False})
        # linear inequation
        cst = Constraint({'x': 1, 'y': 2, 'z': 3}, '<=', 3)
        assert not cst.evaluate({'x': True, 'y': True, 'z': True})
        assert not cst.evaluate({'x': True, 'y': False, 'z': True})
        assert cst.evaluate({'x': True, 'y': False, 'z': False})
        assert cst.evaluate({'x': True, 'y': True, 'z': False})
        # mandatory
        cst = Constraint('x', '<=>', 'y')
        assert cst.evaluate({'x': True, 'y': True})
        assert not cst.evaluate({'x': True, 'y': False})
        assert not cst.evaluate({'x': False, 'y': True})
        assert cst.evaluate({'x': False, 'y': False})
        # dependency
        cst = Constraint('x', '=>', 'y')
        assert cst.evaluate({'x': True, 'y': True})
        assert not cst.evaluate({'x': True, 'y': False})
        assert cst.evaluate({'x': False, 'y': True})
        assert cst.evaluate({'x': False, 'y': False})
        # exclude
        cst = Constraint('x', '><', 'y')
        assert not cst.evaluate({'x': True, 'y': True})
        assert cst.evaluate({'x': True, 'y': False})
        assert cst.evaluate({'x': False, 'y': True})
        assert cst.evaluate({'x': False, 'y': False})
        # or
        cst = Constraint(['x', 'y', 'z'], 'or', 'f')
        assert not cst.evaluate({'x': False, 'y': False, 'z': False, 'f': True})
        assert not cst.evaluate({'x': False, 'y': False, 'z': True, 'f': False})
        assert not cst.evaluate({'x': True, 'y': False, 'z': True, 'f': False})
        assert not cst.evaluate({'x': True, 'y': True, 'z': True, 'f': False})
        assert cst.evaluate({'x': False, 'y': False, 'z': True, 'f': True})
        assert cst.evaluate({'x': True, 'y': True, 'z': True, 'f': True})
        # alt
        cst = Constraint(['x', 'y', 'z'], 'alt', 'f')
        assert not cst.evaluate({'x': False, 'y': False, 'z': False, 'f': True})
        assert not cst.evaluate({'x': False, 'y': False, 'z': True, 'f': False})
        assert not cst.evaluate({'x': True, 'y': False, 'z': True, 'f': False})
        assert not cst.evaluate({'x': True, 'y': True, 'z': True, 'f': False})
        assert not cst.evaluate({'x': True, 'y': True, 'z': True, 'f': True})
        assert not cst.evaluate({'x': True, 'y': False, 'z': True, 'f': True})
        assert cst.evaluate({'x': False, 'y': False, 'z': True, 'f': True})
        assert cst.evaluate({'x': True, 'y': False, 'z': False, 'f': True})

    def test_quadratic_add(self) -> None:
        q = Constraint.quadratic_weighted_add(2, 1,
                                              Quadratic({}, {'x': 1}, 3),
                                              Quadratic({('x', 'y'): 1}, {}, -3))
        assert q.linear == {'x': 2}
        assert q.quadratic == {('x', 'y'): 1}
        assert q.constant == 3
        q = Constraint.quadratic_weighted_add(1, 1,
                                              Quadratic({('y', 'x'): 2}, {'x': 1}, 3),
                                              Quadratic({('x', 'y'): 1}, {'x': 2}, -3))
        assert q.linear == {'x': 3}
        assert q.quadratic == {('y', 'x'): 3} or q.quadratic == {('x', 'y'): 3}
        assert q.constant == 0

    def test_quadratic_qubo(self) -> None:
        self.reset_seed()
        for _ in range(TermTest.LOOP_TIMES):
            qdr = Quadratic(self.random_quadratic_poly(TermTest.VARS_NUM),
                            self.random_linear_poly(TermTest.VARS_NUM),
                            0)
            qubo = Constraint.quadratic_to_qubo_dict(qdr)
            assert len(qubo) == (len(qdr.quadratic) + len(qdr.linear))
            for (k1, k2), v in qubo.items():
                if k1 == k2:
                    assert qdr.linear[k1] == v
                else:
                    assert qdr.quadratic[(k1, k2)] == v
