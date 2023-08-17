package org.osino.Runners;

import java.nio.file.Paths;
import java.nio.file.Path;
import java.util.ArrayList;

import org.uma.jmetal.example.AlgorithmRunner;
import org.osino.Problem;
import org.osino.Results.Results;
import org.osino.Results.Result;
import org.osino.ConfigLoader;
import org.osino.Algorithms.SeededNSGAII;
import org.osino.Constraints.MetaConstraint;

public class CSNSGAII {
    public Results solve(
        Problem problem, int iterations, int populationSize, int maxEvaluations,
        double crossoverProbability, double mutationProbability, ArrayList<String> seeds,
        boolean repair
        ) {
        Results results = new Results();
        for (int i = 0; i < iterations; ++ i) {
            SeededNSGAII algorithm = new SeededNSGAII(problem, iterations, populationSize, maxEvaluations,
                                                      crossoverProbability, mutationProbability, seeds, repair);
            long start = System.nanoTime();
            new AlgorithmRunner.Executor(algorithm).execute();
            long end = System.nanoTime();
            double elapsedTime = (end - start) / 1e9;
            results.put(new Result(elapsedTime, algorithm.getResult()));
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
        assert (config.containsKey("seeds"));
        assert (config.containsKey("repair"));
        assert (config.containsKey("factor"));
        // prepare the problem
        Problem problem = new Problem(config.get("problem"), config.getStringList("objectiveOrder"));
        // add a constraint in the problem, (urgency constraint)
        problem.bicstForm(config.getDouble("factor"));
        // solve
        System.out.println("Cst SNSGA-II solving on " + config.get("problem") + " with factor " + Double.toString(config.getDouble("factor")));
        if (config.getBoolean("repair")) {
            System.out.println("constraints repair is on.");
        }
        SNSGAII algorithm = new SNSGAII();
        Results results = algorithm.solve(
            problem, config.getInteger("iterations"),
            config.getInteger("populationSize"), config.getInteger("maxEvaluations"),
            config.getDouble("crossoverProbability"), config.getDouble("mutationProbability"),
            config.getStringList("seeds"), config.getBoolean("repair")
        );
        // dump
        Path folder = Paths.get(Paths.get(System.getProperty("user.dir")).toString(), "result");
        folder = Paths.get(folder.toString(), config.get("resultFolder"), config.get("problem") + "_" + Double.toString(config.getDouble("factor")));
        folder = Paths.get(folder.toString(), config.get("methodName"));
        results.dump(folder, config.get("methodName"));
    }
}
