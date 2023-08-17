from typing import List, Dict, Tuple
import csv
from matplotlib import pyplot as plt
from jmetal.core.solution import BinarySolution

TableType = List[List[str]]


class Visualizer:
    """ [summary] Visualizer is for visualizing results, involves tabulating, plotting or others.
    """
    @staticmethod
    def tabluate(table: TableType, file_name: str) -> None:
        with open(file_name, 'w+', newline='') as csv_out:
            csv_writer = csv.writer(csv_out)
            csv_writer.writerows(table)

    @staticmethod
    def tabulate_single_problem(problem_name: str, methods: List[str],
                                indicators: List[str], scores: List[Dict[str, float]],
                                indicators_round: Dict[str, int]
                                ) -> TableType:
        """tabulate_single_problem [summary] tabulate results table for a single problem.
        It is about one problem, for the first row, there are indicator names;
        And for the first row, there are methods name.

        <ProblemName>,  <indicator>,    <indicator>,    <indicator>
        <MethodName>,   ...,            ...,            ...
        <MethodName>,   ...,            ...,            ...
        <MethodName>,   ...,            ...,            ...
        """
        table: TableType = [[problem_name] + indicators]
        for method in methods:
            line: List[str] = [method]
            for ind in range(len(indicators)):
                score = str(round(scores[ind][method], indicators_round[indicators[ind]]))
                line.append(score)
            table.append(line)
        return table

    @staticmethod
    def tabulate_multiple_problems(problems: List[str], methods: List[str], indicators: List[str],
                                   head_format: str, scores: List[List[Dict[str, float]]],
                                   indicators_round: Dict[str, int]
                                   ) -> TableType:
        """tabulate_multiple_problems [summary] tabulate results table for multiple problems.
        It is about one problem, for the first row, there are indicator names for every method name;
        And for the first row, there are problem name.

        The format is for how methods and indicators composed.

        <empty>,        <method1-indicator1>,   <method2-indicator1>,   ...,    <m1-ind2>,   <m2-ind2>, ...
        <ProblemName1>, ...,                    ...,                    ...,    ...,        ...,        ...
        <ProblemName2>, ...,                    ...,                    ...,    ...,        ...,        ...
        <ProblemName3>, ...,                    ...,                    ...,    ...,        ...,        ...
        """
        table: TableType = [['']] + [[problem] for problem in problems]
        # head line
        for indicator in indicators:
            for method in methods:
                table[0].append(head_format.format(method, indicator))
        # table content
        for problem_index in range(len(problems)):
            for indicator_index in range(len(indicators)):
                for method in methods:
                    score = str(round(scores[problem_index][indicator_index][method],
                                      indicators_round[indicators[indicator_index]]))
                    table[problem_index + 1].append(score)
        return table

    @staticmethod
    def scatter(x: List[float], y: List[float], label: str = '',
                annotation: List[str] = [], file_name: str = '') -> None:
        """scatter [summary] plot 2d archive.

        Annotation is labeled accordingly to the points if given.

        Save the figure as file if file_name is assigned.
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(x, y, s=10, c='b', marker=".", label=label)
        for i, anno in enumerate(annotation):
            ax.annotate(anno, (x[i], y[i]))
        plt.legend(loc='upper left')
        if file_name == '':
            plt.show()
        else:
            plt.savefig(file_name)

    @staticmethod
    def scatter2(x1: List[float], y1: List[float], x2: List[float], y2: List[float],
                 label1: str = '', annotation1: List[str] = [],
                 label2: str = '', annotation2: List[str] = [],
                 file_name: str = '') -> None:
        """scatter2 [summary] plot 2 2d archives.

        Annotation is labeled accordingly to the points if given.

        Save the figure as file if file_name is assigned.
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(x1, y1, s=10, c='b', marker="o", label=label1)
        ax.scatter(x2, y2, s=10, c='r', marker="x", label=label2)
        for i, anno in enumerate(annotation1):
            ax.annotate(anno, (x1[i], y1[i]))
        for i, anno in enumerate(annotation2):
            ax.annotate(anno, (x2[i], y2[i]))
        plt.legend(loc='upper left')
        if file_name == '':
            plt.show()
        else:
            plt.savefig(file_name)

    @staticmethod
    def project(solutions: List[BinarySolution],
                x_index: int = 0, y_index: int = 1) -> Tuple[List[float], List[float]]:
        """project [summary] project solutions objectives to x and y value list,
        which are indicated by the x_index and y_index.
        """
        x = [s.objectives[x_index] for s in solutions]
        y = [s.objectives[y_index] for s in solutions]
        return (x, y)

    @staticmethod
    def scatter_n(n: int, xs: List[List[float]], ys: List[List[float]],
                  labels: List[str], annoations: List[List[str]] = [],
                  file_name: str = '') -> None:
        """scatter_n [summary] plot n 2d archives.

        Annotation is labeled accordingly to the points if given.

        Save the figure as file if file_name is assigned.
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for i in range(n):
            ax.scatter(xs[i], ys[i], s=10, label=labels[i])
            if annoations == []: continue
            for j, anno in enumerate(annoations[i]):
                ax.annotate(anno, (xs[i][j], ys[i][j]))
        plt.legend(loc='upper left')
        if file_name == '':
            plt.show()
        else:
            plt.savefig(file_name)

    @staticmethod
    def line_chart_elapsed_n(problems_name: List[str], methods: List[str],
                    scores: List[List[Dict[str, float]]],
                    indicators_round: int,
                    file_name: str = '',
                    ):
        """line_chart_n [summary] plot n 2d archives.

        Annotation is labeled accordingly to the points if given.

        Save the figure as file if file_name is assigned.
        """
        # ax = fig.add_subplot(111)
        n = len(problems_name)
        x = [0.3, 0.5, 0.7, 0.9, 1.0]
        style = ['g*-', 'r*-', 'k*-', 'b*-']

        for problem_index in range(len(problems_name)):
            y = []
            for method in methods:
                score = str(round(scores[problem_index][0][method],
                                indicators_round))
                y.append(score)
            for x_, y_ in zip(x, y):
                plt.text(x_, y_+0.3, '%.00f' % y, ha='center', va='bottom', fontsize=7.5)

            plt.plot(x, y, style[problem_index], alpha=0.5, linewidth=1, label=problems_name[problem_index])#'bo-'表示蓝色实线，数据点实心原点标注

            plt.legend()  
            plt.xlabel('Rate of Sub-problems Participating in QA Solution') 
            plt.ylabel('Elapsed Time (s)')
            
            #plt.ylim(-1,1)#仅设置y轴坐标范围
            plt.show()
            plt.savefig(file_name)
