# -*- coding: utf-8 -*-
"""
Created on Sun Aug 09 16:40:34 2020

@author: allen
"""

import sys, os
import numpy as np
from typing import List, Dict, Set
from jmetal.core.solution import FloatSolution, Solution
from jmetal.core.quality_indicator import QualityIndicator


class EvennessIndicator(QualityIndicator):
    def __init__(self, reference_front: np.array = None):
        super(EvennessIndicator, self).__init__(is_minimization=True)
        self.reference_front = reference_front

    def compute(self, solutions) -> float:
        size = len(solutions)
        if size <= 1:
            return -1.0
        neighbourPair : Dict[int, int] = {}
        neighbourDist : Dict[int, float] = {}
        
        'i denotes the current point'
        for i in range(size): 
            'j denotes the searching point'
            currDist= sys.float_info.max
            for j in range(size): 
                if (i==j):
                    continue
                # dist =  np.linalg.norm(np.array(solutions[i].objectives) - np.array(solutions[j].objectives))
                dist =  np.linalg.norm(solutions[i] - solutions[j])
                if(dist < currDist):
                    currDist = dist
                    neighbourPair[i] = j
                    neighbourDist[i] = currDist
                    
        'calculate average neightdistance'
        dist_list = list(neighbourDist.values())
        mean_dist = np.mean(dist_list) 
        'calculate the evennesss'
        '''
        see the paper: Schott JR (1995) Fault tolerant design using single and multicriteria genetic algorithm
        optimization. Master’s thesis, Massachusetts Institute of Technology
        '''
        evenness = np.sqrt(sum(map(lambda dist: pow(dist-mean_dist,2), dist_list))/ (size-1))
        del neighbourPair
        del neighbourDist
        return  evenness

    def get_short_name(self) -> str:
        return 'E'

    def get_name(self) -> str:
        return "Evenness"

if __name__ == "__main__":
        os._exit(0) 
else:
    pass
    # print("evenness_indicator.py is being imported into another module")