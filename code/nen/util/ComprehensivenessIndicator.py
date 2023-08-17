#
# DONG Shi, dongshi@mail.ustc.edu.cn
# ComprehensivenessIndicator.py, created: 2020.11.10
# last modified: 2020.11.11
#

from typing import List
import numpy as np
from statistics import median
from jmetal.core.quality_indicator import QualityIndicator


class MeanIndicator(QualityIndicator):
    def __init__(self) -> None:
        super().__init__(is_minimization=True)

    def compute(self, solutions: np.array) -> float:
        distance = 0.0
        for i in solutions:
            for j in solutions:
                distance += np.linalg.norm(i - j)
        return distance / len(solutions)

    def get_name(self) -> str:
        return 'MN'

    def get_short_name(self) -> str:
        return 'Mean'


class MedianIndicator(QualityIndicator):
    def __init__(self) -> None:
        super().__init__(is_minimization=True)

    def compute(self, solutions: np.array) -> float:
        distance: List[float] = []
        for i in solutions:
            for j in solutions:
                distance.append(np.linalg.norm(i - j))
        return median(distance)

    def get_name(self) -> str:
        return 'MD'

    def get_short_name(self) -> str:
        return 'Midean'
