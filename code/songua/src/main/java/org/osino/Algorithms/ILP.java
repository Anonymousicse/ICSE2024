package org.osino.Algorithms;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

import org.uma.jmetal.util.archive.impl.NonDominatedSolutionListArchive;

import org.osino.CBSolution;
import org.osino.Problem;
import org.osino.Constraints.MetaConstraint;
import org.osino.Constraints.Optional;
import org.osino.Constraints.LinearInequation;

import ilog.concert.IloException;
import ilog.concert.IloIntVar;
import ilog.concert.IloObjective;
import ilog.cplex.IloCplex;
import ilog.concert.IloRange;


public class ILP {
    private Problem problem;
    private IloCplex solver;
    private IloIntVar[] variables;
    private HashMap<String, Integer> variablesIndex;
    private Random random = new Random(System.currentTimeMillis());

    public Problem getProblem() { return problem; }
    public void setProblem(Problem problem) { this.problem = problem; }
    public IloCplex getSolver() { return solver; }
    public void setSolver(IloCplex solver) { this.solver = solver; }
    public IloIntVar[] getVariables() { return variables; }
    public void setVariables(IloIntVar[] variables) { this.variables = variables; }
    public HashMap<String, Integer> getVariablesIndex() { return variablesIndex; }
    public void setVariablesIndex(HashMap<String, Integer> variablesIndex) { this.variablesIndex = variablesIndex; }


    ILP(Problem problem, double timeLimit) {
        this.problem = problem;
        try {
            this.solver = new IloCplex();
            this.solver.setOut(null);
			// this.solver.setParam(IloCplex.Param.MIP.Tolerances.AbsMIPGap, 0.0);
			// this.solver.setParam(IloCplex.Param.MIP.Tolerances.MIPGap, 0.0);
			this.solver.setParam(IloCplex.Param.Threads, 1);
			// cplex.setParam(IloCplex.Param.Parallel, 0);
            this.solver.setParam(IloCplex.Param.TimeLimit, timeLimit);

            // variables
            this.variables = this.solver.boolVarArray(problem.getVariables().size());
            // mapping variables -> index
            this.variablesIndex = new HashMap<String, Integer>();
            for (int i = 0; i < this.variables.length; ++ i) {
                this.variablesIndex.put(problem.getVariables().get(i), i);
            }
            // add constraints
            for (MetaConstraint constraint: problem.getConstraints().getConstraintList()) {
                this.addConstraint(constraint);
            }
        } catch (IloException e) {
            System.err.println("Cplex initialize: " + e);
        }
    }

    public IloRange addConstraint(MetaConstraint constraint) {
        try {
            // TODO: support more constraints!
            if (constraint instanceof LinearInequation) {
                LinearInequation cst = (LinearInequation) constraint;
                HashMap<String, Double> left = cst.getLeft();
                double right = cst.getRight();
                // Linear Inequation maintain
                IloIntVar[] vars = new IloIntVar[left.size()];
                double[] coefs = new double[left.size()];
                int index = 0;
                for (Map.Entry<String, Double> entry: left.entrySet()) {
                    String varName = entry.getKey();
                    vars[index] = this.variables[this.variablesIndex.get(varName)];
                    coefs[index] = entry.getValue();
                    index += 1;
                }
                // add the constraint
                return this.solver.addLe(this.solver.scalProd(vars, coefs), right);
            } else if (constraint instanceof Optional) {
                Optional cst = (Optional) constraint;
                String left = cst.getLeft();
                String right = cst.getRight();
                // left - right <= 0
                IloIntVar[] vars = new IloIntVar[2];
                double[] coefs = new double[2];
                vars[0] = this.variables[this.variablesIndex.get(left)];
                vars[1] = this.variables[this.variablesIndex.get(right)];
                coefs[0] = 1; coefs[1] = -1;
                // add the constraint
                return this.solver.addLe(this.solver.scalProd(vars, coefs), 0);
            } else {
                assert false;
                return null;
            }
        } catch (IloException e) {
            System.err.println("addConstraint: " + e);
            return null;
        }
    }

    public void setMinimize(HashMap<String, Double> objective) {
        try {
            IloIntVar[] vars = new IloIntVar[objective.size()];
            double[] coefs = new double[objective.size()];
            int index = 0;
            for (Map.Entry<String, Double> entry: objective.entrySet()) {
                vars[index] = this.variables[this.variablesIndex.get(entry.getKey())];
                coefs[index] = entry.getValue();
                index += 1;
            }
            this.solver.addMinimize(this.solver.scalProd(vars, coefs));
        } catch (IloException e) {
            System.err.println("setMinimize: " + e);
        }
    }

    public HashMap<String, Boolean> minimizeOnce(HashMap<String, Double> objective) {
        try {
            IloIntVar[] vars = new IloIntVar[objective.size()];
            double[] coefs = new double[objective.size()];
            int index = 0;
            for (Map.Entry<String, Double> entry: objective.entrySet()) {
                vars[index] = this.variables[this.variablesIndex.get(entry.getKey())];
                coefs[index] = entry.getValue();
                index += 1;
            }
            IloObjective obj = this.solver.addMinimize(this.solver.scalProd(vars, coefs));
            if (this.solver.solve()) {
                HashMap<String, Boolean> values = this.emptyValues();
                ArrayList<String> varNames = this.problem.getVariables();
                double[] val = this.solver.getValues(this.variables);
                for (int i = 0; i < this.variables.length; ++ i) {
                    values.put(varNames.get(i), (val[i] > 0.5));
                }
                this.solver.remove(obj);
                return values;
            } else {
                this.solver.remove(obj);
                return null;
            }
        } catch (IloException e) {
            System.err.println("minimizeOnce: " + e);
            return null;
        }
    }

    public HashMap<String, Boolean> emptyValues() {
        HashMap<String, Boolean> values = new HashMap<String, Boolean>();
        for (String var: this.problem.getVariables()) {
            values.put(var, false);
        }
        return values;
    }

    public HashMap<String, Boolean> solve() {
        HashMap<String, Boolean> values = this.emptyValues();
        ArrayList<String> varNames = this.problem.getVariables();
        try {
            if (this.solver.solve()) {
                double[] val = this.solver.getValues(this.variables);
                for (int i = 0; i < this.variables.length; ++ i) {
                    values.put(varNames.get(i), (val[i] > 0.5));
                }
                return values;
            } else {
                return null;
            }
        } catch (IloException e) {
            System.err.println("solve: " + e);
            return null;
        }
    }

    public NonDominatedSolutionListArchive<CBSolution> emptyArchive() {
        return new NonDominatedSolutionListArchive<CBSolution>();
    }

    public double lowerBound(HashMap<String, Double> objective) {
        double lb = 0;
        for (double val: objective.values()) {
            if (val < 0) {
                lb += val;
            }
        }
        return lb;
    }

    public double upperBound(HashMap<String, Double> objective) {
        double ub = 0;
        for (double val: objective.values()) {
            if (val > 0) {
                ub += val;
            }
        }
        return ub;
    }

    public String arrayString(double[] arr) {
        String s = "";
        boolean first = true;
        for (double e: arr) {
            if (first) {
                first = false;
            } else {
                s += " ";
            }
            s += Double.toString(e);
        }
        return s;
    }

    public HashMap<String, Double> weightedSum(HashMap<String, HashMap<String, Double>> objectives, HashMap<String, Double> weights) {
        HashMap<String, Double> obj = new HashMap<String, Double>();
        for (Map.Entry<String, HashMap<String, Double>> entry: objectives.entrySet()) {
            String name = entry.getKey();
            HashMap<String, Double> objective = entry.getValue();
            double weight = weights.get(name);

            for (Map.Entry<String, Double> term: objective.entrySet()) {
                String var = term.getKey();
                double coef = term.getValue();
                if (obj.containsKey(var)) {
                    obj.put(var, (obj.get(var) + (weight * coef)));
                } else {
                    obj.put(var, (weight * coef));
                }
            }
        }
        return obj;
    }

    public HashMap<String, Boolean> randomWeightedSumSolve(HashMap<String, HashMap<String, Double>> objectives) {
        // random weights
        HashMap<String, Double> weights = new HashMap<String, Double>();
        for (String name: objectives.keySet()) {
            weights.put(name, this.random.nextDouble());
        }
        // weighted sum
        HashMap<String, Double> objective = this.weightedSum(objectives, weights);
        // solve
        return this.minimizeOnce(objective);
    }

    public static void main(String[] args) {
        ArrayList<String> order = new ArrayList<String>();
        order.add("revenue"); order.add("cost");
        Problem problem = new Problem("classic-1", order);
        ILP ilp = new ILP(problem, 100);
        for (int i = 0; i < 50; ++ i) {
            HashMap<String, Boolean> values = ilp.randomWeightedSumSolve(problem.getObjectives());
            if (values != null) {
                CBSolution solution = problem.createSolution(values);
                problem.evaluate(solution);
                System.out.println(ilp.arrayString(solution.getObjectives()));
            } else {
                System.out.println("infeasible");
            }
        }
    }

    public static void main2(String[] args) {
        ArrayList<String> order = new ArrayList<String>();
        order.add("revenue"); order.add("cost");
        Problem problem = new Problem("classic-1", order);
        ILP ilp = new ILP(problem, 1000000);
        HashMap<String, Double> costObj = problem.getObjectives().get("cost");
        // ilp.setMinimize(problem.getObjectives().get("revenue"));
        NonDominatedSolutionListArchive<CBSolution> archive = ilp.emptyArchive();
        double lb = ilp.lowerBound(costObj);
        double ub = ilp.upperBound(costObj);
        try {
            IloRange costCst = ilp.addConstraint(new LinearInequation(costObj, 0.0));
            int rhs = (int)(Math.ceil(ub));
            while (rhs >= lb) {
                costCst.setUB(rhs);
                // HashMap<String, Boolean> values = ilp.solve();
                HashMap<String, Boolean> values = ilp.minimizeOnce(problem.getObjectives().get("revenue"));
                CBSolution solution = problem.createSolution(values);
                // CBSolution solution = problem.createSolution();
                // int index = 0;
                // for (String varName: problem.getVariables()) {
                //     solution.setOneBitVariable(index, values.get(varName));
                //     index += 1;
                // }
                problem.evaluate(solution);
                archive.add(solution);
                rhs -= 1;
            }
        } catch (IloException e) {
            System.err.println("main: " + e);
        }
        System.out.println(archive.size());
    }
}
