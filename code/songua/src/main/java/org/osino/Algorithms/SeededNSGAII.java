package org.osino.Algorithms;

import org.uma.jmetal.algorithm.multiobjective.nsgaii.NSGAII;
import org.uma.jmetal.solution.binarysolution.BinarySolution;
import org.uma.jmetal.util.comparator.RankingAndCrowdingDistanceComparator;
import org.uma.jmetal.util.evaluator.impl.SequentialSolutionListEvaluator;

import org.uma.jmetal.operator.selection.impl.NaryTournamentSelection;
import org.uma.jmetal.operator.mutation.impl.BitFlipMutation;
import org.uma.jmetal.operator.crossover.impl.SinglePointCrossover;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
// import java.util.Random;

import org.osino.Problem;
import org.osino.CBSolution;
import org.osino.Constraints.Constraints;
import org.osino.Constraints.Optional;
import org.osino.Constraints.MetaConstraint;

public class SeededNSGAII extends NSGAII<BinarySolution>{
    private static final long serialVersionUID = 1L;
    // private Random randomGenerator;
    private Problem myProblem;
    private ArrayList<String> seeds;
    private HashMap<String, Integer> variablesIndex;
    private boolean repair;

    // constructor
    public SeededNSGAII(
        Problem problem, int iterations, int populationSize, int maxEvaluations,
        double crossoverProbability, double mutationProbability, ArrayList<String> seeds,
        boolean repair
    ) {
        super(problem, maxEvaluations, populationSize, populationSize, populationSize,
              new SinglePointCrossover(crossoverProbability),
              new BitFlipMutation(mutationProbability),
              new NaryTournamentSelection<BinarySolution>(5, new RankingAndCrowdingDistanceComparator<BinarySolution>()),
              new SequentialSolutionListEvaluator<BinarySolution>()
              );

        this.myProblem = problem;
        this.seeds = seeds;
        this.repair = repair;
        // // prepare random generator
        // this.randomGenerator = new Random(System.currentTimeMillis());
        // prepare variables index
        this.variablesIndex = new HashMap<String, Integer>();
        for (int i = 0; i < this.myProblem.getNumberOfVariables(); ++ i) {
            String variable = this.myProblem.getVariables().get(i);
            this.variablesIndex.put(variable, i);
        }
    }

    @Override protected List<BinarySolution> createInitialPopulation() {
        // this.randomGenerator = new Random(System.currentTimeMillis());
        List<BinarySolution> population = new ArrayList<>(getMaxPopulationSize());
        for (int i = 0; i < this.seeds.size(); ++ i) {
            CBSolution solution = this.myProblem.createSolution(this.seeds.get(i));
            population.add(solution);
        }
        for (int i = this.seeds.size(); i < getMaxPopulationSize(); i++) {
            CBSolution solution = this.myProblem.createSolution();
            population.add(solution);
        }
        return population;
    }

    private void repairEvaluate(BinarySolution solution) {
        // prepare constraints
        Constraints constraints = this.myProblem.getConstraints();
        // get variable -> boolean mapping
        HashMap<String, Boolean> values = this.myProblem.getValues(solution);
        for (int k = 0; k < constraints.size(); ++ k) {
            MetaConstraint constraint_ = constraints.get(k);
            // only repair Optional, a.k.a. dependency
            // NOTE: IT JUST WORKS WHEN ALL OPTIONAL CONSTRAINTS ARE BEFORE OTHER TYPES CONSTRAINTS
            if (constraint_ instanceof Optional) {
                // repair
                // x => y violate (x: 1, y: 0), set y = 1
                Optional constraint = (Optional)constraint_;
                int left = this.variablesIndex.get(constraint.getLeft());
                int right = this.variablesIndex.get(constraint.getRight());
                if (solution.getVariable(left).get(0) && (!solution.getVariable(right).get(0))) {
                    solution.getVariable(right).set(0, true);
                }
                solution.setConstraint(k, 0.0);
            } else {
                // evaluate
                if (!constraint_.evaluate(values)) {
                    solution.setConstraint(k, -1.0);
                } else {
                    solution.setConstraint(k, 0.0);
                }
            }
        }
        // evaluate objectives
        this.myProblem.evaluateObjective(solution);
    }

    @Override protected List<BinarySolution> evaluatePopulation(List<BinarySolution> population) {
        for (int index = 0; index < population.size(); ++ index) {
            // for each solution
            BinarySolution solution = population.get(index);
            if (this.repair) {
                this.repairEvaluate(solution);
            } else {
                this.myProblem.evaluate(solution);
            }
        }
        return population;
    }
}

