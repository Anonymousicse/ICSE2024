import unittest
from nen.Visualizer import Visualizer


class VisualizerTest(unittest.TestCase):
    def test_tabulating(self) -> None:
        # single problem
        table = Visualizer.tabulate_single_problem('problem', ['m1', 'm2', 'm3'], ['i1', 'i2', 'i3'],
                                                   [{'m1': 0.03333, 'm2': 1.777, 'm3': 4.999},
                                                    {'m1': 1.11111, 'm2': 2.222, 'm3': 3},
                                                    {'m1': 3, 'm2': 5, 'm3': 7.7777}],
                                                   {'i1': 2, 'i2': 1, 'i3': 0})
        Visualizer.tabluate(table, 'tmp1.csv')
        # multiple problems
        table = \
            Visualizer.tabulate_multiple_problems(
                ['p1', 'p2', 'p3'], ['m1', 'm2'], ['i1', 'i2', 'i3', 'i4'], '{}+{}',
                [
                    [{'m1': 1.1, 'm2': 1.2}, {'m1': 1.3, 'm2': 1.4}, {'m1': 1.5, 'm2': 1.6}, {'m1': 1.7, 'm2': 1.8}],
                    [{'m1': 2.1, 'm2': 2.2}, {'m1': 2.3, 'm2': 2.4}, {'m1': 2.5, 'm2': 2.6}, {'m1': 2.7, 'm2': 2.8}],
                    [{'m1': 3.1, 'm2': 3.2}, {'m1': 3.3, 'm2': 3.4}, {'m1': 3.5, 'm2': 3.6}, {'m1': 3.7, 'm2': 3.8}]
                ],
                {'i1': 1, 'i2': 2, 'i3': 1, 'i4': 0}
            )
        Visualizer.tabluate(table, 'tmp2.csv')
