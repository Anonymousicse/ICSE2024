package org.osino.Runners;

import java.nio.file.Paths;
import java.nio.file.Path;
import java.util.List;
import org.uma.jmetal.algorithm.Algorithm;
import org.uma.jmetal.example.AlgorithmRunner;
import org.uma.jmetal.solution.binarysolution.BinarySolution;
import org.uma.jmetal.operator.mutation.impl.BitFlipMutation;
import org.uma.jmetal.operator.crossover.impl.SinglePointCrossover;
import org.uma.jmetal.operator.selection.impl.BinaryTournamentSelection;
import org.uma.jmetal.algorithm.multiobjective.nsgaii.NSGAIIBuilder;

import org.osino.Problem;
import org.osino.Results.Results;
import org.osino.Results.Result;
import org.osino.ConfigLoader;

public class NSGAII {
    public Results solve(
        Problem problem, int iterations, int populationSize, int maxEvaluations,
        double crossoverProbability, double mutationProbability, double exec_time
        ) {
        Results results = new Results();
        long s = System.nanoTime();
        for (int i = 0; i < iterations; ++ i) {
            Algorithm<List<BinarySolution>> algorithm = new NSGAIIBuilder<BinarySolution>(
                problem,
                new SinglePointCrossover(crossoverProbability), 
                new BitFlipMutation(mutationProbability),
                populationSize
                )
                .setSelectionOperator(new BinaryTournamentSelection<BinarySolution>())
                .setMaxEvaluations(maxEvaluations)
                .build();
            long start = System.nanoTime();
            new AlgorithmRunner.Executor(algorithm).execute();
            long end = System.nanoTime();
            double elapsedTime = (end - start) / 1e9;
            results.put(new Result(elapsedTime, maxEvaluations, algorithm.getResult()));
            if (exec_time > 0)
                if (System.nanoTime() - s > exec_time) break;
        }
        return results;
    }

    public static void main(String[] args) {
        // handle the arguments and get the config
        assert (args.length == 1);
        ConfigLoader config = new ConfigLoader(args[0]);
        // check arguments
        assert (config.containsKey("problem"));
        assert (config.containsKey("objectiveOrder"));
        assert (config.containsKey("iterations"));
        assert (config.containsKey("populationSize"));
        assert (config.containsKey("maxEvaluations"));
        assert (config.containsKey("crossoverProbability"));
        assert (config.containsKey("mutationProbability"));
        assert (config.containsKey("resultFolder"));
        assert (config.containsKey("methodName"));
        // run the algorithm
        Problem problem;
        if (config.containsKey("initial_solution")){
            problem = new Problem(config.get("problem"), config.getStringList("objectiveOrder"));
        }
        else  {
            problem = new Problem(config.get("problem"), config.getStringList("objectiveOrder"));
        }
        System.out.println("NSGA-II solving on " + config.get("problem"));
        NSGAII algorithm = new NSGAII();
        // dump the results
        Results results =
            algorithm.solve(problem, config.getInteger("iterations"),
                            config.getInteger("populationSize"), config.getInteger("maxEvaluations"),
                            config.getDouble("crossoverProbability"), config.getDouble("mutationProbability"),
                            config.getDouble("exec_time")
                            );
        Path folder = Paths.get(Paths.get(System.getProperty("user.dir")).toString(), "result");
        folder = Paths.get(folder.toString(), config.get("resultFolder"), config.get("problem"));
        folder = Paths.get(folder.toString(), config.get("methodName"));
        results.dump(folder, config.get("methodName"));
    }
}
