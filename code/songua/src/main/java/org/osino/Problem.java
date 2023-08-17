package org.osino;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.HashMap;
import java.util.Map.Entry;

import java.util.ArrayList;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.TypeReference;
import org.uma.jmetal.solution.binarysolution.BinarySolution;
import org.uma.jmetal.problem.binaryproblem.impl.AbstractBinaryProblem;
import org.osino.Constraints.Constraints;
import org.osino.Constraints.LinearInequation;
import org.osino.Constraints.MetaConstraint;

public class Problem extends AbstractBinaryProblem {
    private static final long serialVersionUID = 1L;
    private List<Integer> bitsPerVariable;

    private ArrayList<String> variables;
    private HashMap<String, HashMap<String, Double>> objectives;
    private Constraints constraints;
    private ArrayList<String> objectiveOrder;

    public ArrayList<String> getVariables() { return variables; }
    public void setVariables(ArrayList<String> variables) { this.variables = variables; }
    public HashMap<String, HashMap<String, Double>> getObjectives() { return objectives; }
    public void setObjectives(HashMap<String, HashMap<String, Double>> objectives) { this.objectives = objectives; }
    public Constraints getConstraints() { return constraints; }
    public void setConstraints(Constraints constraints) { this.constraints = constraints; }
    public ArrayList<String> getObjectiveOrder() { return objectiveOrder; }
    public void setObjectiveOrder(ArrayList<String> objectiveOrder) {
        assert objectiveOrder.size() > 0;
        for (String objectiveName: objectiveOrder) {
            assert this.objectives.containsKey(objectiveName);
        }
        this.objectiveOrder = objectiveOrder;
        this.setNumberOfObjectives(this.objectiveOrder.size());
    }

    public Problem(String name, ArrayList<String> objectiveOrder) {
        Path dataFolder = Paths.get(Paths.get(System.getProperty("user.dir")).toString(), "data");
        Path fileName = Paths.get(dataFolder.toString(), name + ".json");
        try {
            String content = Files.readString(fileName, StandardCharsets.US_ASCII);
            HashMap<String, String> problem = JSON.parseObject(content,  new TypeReference<HashMap<String, String>>(){});
            // variables
            this.variables = JSON.parseObject(problem.get("variables"), new TypeReference<ArrayList<String>>(){});
            // objectives
            this.objectives = JSON.parseObject(problem.get("objectives"),  new TypeReference<HashMap<String, HashMap<String, Double>>>(){});
            // constraints
            this.constraints = new Constraints();
            ArrayList<ArrayList<String>> constraints = JSON.parseObject(problem.get("constraints"), new TypeReference<ArrayList<ArrayList<String>>>(){});
            for (ArrayList<String> constraintString: constraints) {
                assert constraintString.size() == 3;
                String leftString = constraintString.get(0);
                String sense = constraintString.get(1);
                String rightString = constraintString.get(2);
                this.constraints.add(leftString, sense, rightString);
            }
            // set number of variables, objectives and constraints
            // set name, bitsPerVariable
            postInitialize(name);
            // set objectiveOrder
            if (objectiveOrder.size() == 0) {
                for (String objectiveName: this.objectives.keySet()) {
                    objectiveOrder.add(objectiveName);
                }
            }
            setObjectiveOrder(objectiveOrder);
        } catch (IOException e) {
            System.out.println("cannot find problem " + name);
        }
    }

    public void postInitialize(String name) {
        setNumberOfVariables(this.variables.size());
        setNumberOfConstraints(this.constraints.size());
        setNumberOfObjectives(this.objectives.size());
        setName(name);
        bitsPerVariable = new ArrayList<>(this.variables.size());
        for (int var = 0; var < this.variables.size(); var ++) {
            bitsPerVariable.add(1);
        }
    }

    @Override
    public List<Integer> getListOfBitsPerVariable() {
        return bitsPerVariable;
    }

    @Override
    public String toString() {
        String content = "";
        // variables
        content += "variables:\n";
        content += this.variables.toString();
        content += "objectives:\n";
        for (HashMap.Entry<String, HashMap<String, Double>> pair : this.objectives.entrySet()) {
            content += ("\t" + pair.getKey() + ": ");
            content += pair.getValue().toString();
            content += "\n";
        }
        content += "constraints:\n";
        for (MetaConstraint cst: this.constraints.getConstraintList()) {
            content += (cst.toString() + "\n");
        }
        return content;
    }

    public HashMap<String, Boolean> getValues(BinarySolution solution) {
        HashMap<String, Boolean> values = new HashMap<String, Boolean>();
        for (int i = 0; i < this.variables.size(); ++ i) {
            values.put(this.variables.get(i), solution.getVariable(i).get(0));
        }
        return values;
    }

    public void evaluateObjective(BinarySolution solution) {
        HashMap<String, Boolean> values = this.getValues(solution);
        // calculate obecjectives
        for (int i = 0; i < this.objectiveOrder.size(); ++ i) {
            String objectiveName = this.objectiveOrder.get(i);
            HashMap<String, Double> objective = this.objectives.get(objectiveName);
            double obj = 0.0;
            for (Entry<String, Double> kv: objective.entrySet()) {
                if (values.get(kv.getKey())) {
                    obj += kv.getValue();
                }
            }
            solution.setObjective(i, obj);
        }
    }

    public void evaluateConstraint(BinarySolution solution) {
        HashMap<String, Boolean> values = this.getValues(solution);
        // set solution constraint
        for (int i = 0; i < this.constraints.size(); ++ i) {
            MetaConstraint constraint = this.constraints.get(i);
            if (!constraint.evaluate(values)) {
                solution.setConstraint(i, -1.0);
            } else {
                solution.setConstraint(i, 0.0);
            }
        }
    }

    public void evaluate(BinarySolution solution) {
        HashMap<String, Boolean> values = this.getValues(solution);
        // calculate obecjectives
        for (int i = 0; i < this.objectiveOrder.size(); ++ i) {
            String objectiveName = this.objectiveOrder.get(i);
            HashMap<String, Double> objective = this.objectives.get(objectiveName);
            double obj = 0.0;
            for (Entry<String, Double> kv: objective.entrySet()) {
                if (values.get(kv.getKey())) {
                    obj += kv.getValue();
                }
            }
            solution.setObjective(i, obj);
        }
        // set solution constraint
        for (int i = 0; i < this.constraints.size(); ++ i) {
            MetaConstraint constraint = this.constraints.get(i);
            if (!constraint.evaluate(values)) {
                solution.setConstraint(i, -1.0);
            } else {
                solution.setConstraint(i, 0.0);
            }
        }
    }

    @Override
    public CBSolution createSolution() {
        CBSolution solution = new CBSolution(getListOfBitsPerVariable(), getNumberOfObjectives(), getNumberOfConstraints());
        return solution;
    }

    public CBSolution createSolution(HashMap<String, Boolean> values) {
        CBSolution solution = new CBSolution(getListOfBitsPerVariable(), getNumberOfObjectives(), getNumberOfConstraints());
        for (int i = 0; i < this.getNumberOfVariables(); ++ i) {
            String var = this.variables.get(i);
            solution.setOneBitVariable(i, values.get(var));
        }
        return solution;
    }

    public CBSolution createSolution(String values) {
        CBSolution solution = new CBSolution(getListOfBitsPerVariable(), getNumberOfObjectives(), getNumberOfConstraints());
        for (int i = 0; i < this.getNumberOfVariables(); ++ i) {
            solution.setOneBitVariable(i, (values.charAt(i) == '1'));
        }
        return solution;
    }

    // TODO: REMOVE THIS METHOD! IT IS JUST FOR THE NRP BI-CST FORMULATION
    public void bicstForm(double factor) {
        // add a constraint from urgency
        assert this.objectives.containsKey("urgency");
        HashMap<String, Double> left = this.objectives.get("urgency");
        double sum = 0.0;
        for (double coef: left.values()) {
            sum += coef;
        }
        this.constraints.add(new LinearInequation(left, sum * factor));
        // remove urgency objective
        this.objectives.remove("urgency");
        this.objectiveOrder.remove("urgency");
        assert (this.objectives.size() == 2);
        assert (this.objectiveOrder.size() == 2);
        setNumberOfConstraints(this.constraints.size());
        setNumberOfObjectives(this.objectives.size());
    }
}
