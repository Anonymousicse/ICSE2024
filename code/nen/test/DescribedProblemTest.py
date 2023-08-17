import unittest
from typing import List, Dict, Any
from copy import deepcopy
from os import remove, path
from nen.DescribedProblem import DescribedProblem


class DescribedProblemTest(unittest.TestCase):
    def test_dump_load(self) -> None:
        """test_dump_load [summary] test dump to and load from described problem files
        """
        variables: List[str] = ['x1', 'x2', 'x3', 'x4', 'x5', 'x6']
        objectives: Dict[str, Dict[str, float]] = {
            'obj1': {'x1': 1, 'x2': 2, 'x3': 3},
            'obj2': {'x4': -1.5, 'x5': -2.5, 'x6': -3.5},
            'obj3': {'x1': 1, 'x3': 1, 'x6': 1}
        }
        constraints: List[List[Any]] = [
            [['x1', 'x2'], 'or', 'x3'],
            [{'x3': 2.3, 'x4': 3.5}, '=', 2],
            ['x5', '><', 'x6']
        ]
        problem = DescribedProblem()
        problem.variables = deepcopy(variables)
        problem.objectives = deepcopy(objectives)
        problem.constraints = deepcopy(constraints)
        # dump
        problem.dump('test')
        # load
        problem_another = DescribedProblem()
        problem_another.load('test')
        # check
        assert problem_another.variables == variables
        assert problem_another.objectives == objectives
        assert problem_another.constraints == constraints
        # remove file
        remove(path.join(DescribedProblem.DATA_PATH, 'test.json'))
