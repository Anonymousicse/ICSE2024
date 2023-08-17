package org.osino.Results;

import java.util.List;
import java.util.ArrayList;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.Files;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import org.uma.jmetal.util.binarySet.BinarySet;
import org.uma.jmetal.solution.binarysolution.BinarySolution;


public class Result {
    private double elapsedTime;
    private List<BinarySolution> solutions;
    private double num_anneals;

    public Result () {}
    public Result (double elapsedTime, List<BinarySolution> solutions) {
        setElapsedTime(elapsedTime);
        setSolutions(solutions);
    }
    public Result (double elapsedTime, double num_anneals, List<BinarySolution> solutions) {
        setElapsedTime(elapsedTime);
        setSolutions(solutions);
        setTotal_num_anneals(num_anneals);
    }

    public double getElapsedTime() {
        return elapsedTime;
    }
    public void setElapsedTime(double elapsedTime) {
        this.elapsedTime = elapsedTime;
    }
    public void setTotal_num_anneals(double num_anneals) {
        this.num_anneals = num_anneals;
    }
    public double getTotal_num_anneals() {
        return num_anneals;
    }
    public List<BinarySolution> getSolutions() {
        return solutions;
    }
    public void setSolutions(List<BinarySolution> solutions) {
        this.solutions = new ArrayList<BinarySolution>();
        for (BinarySolution solution: solutions) {
            int violated = 0;
            for (double cst: solution.getConstraints()) {
                if (cst < 0.0) { violated ++; }
            }
            if (violated == 0) {
                this.solutions.add(solution);
            }
        }
    }


    public static String booleanListToString (List<Boolean> list) {
        String str = "";
        for (boolean element: list) {
            if (element) { str += "1"; }
            else { str += "0"; }
        }
        return str;
    }

    public static String doubleListToString (double[] list) {
        String str = "";
        boolean first = true;
        for (double element: list) {
            if (first) { first = false; }
            else { str += " "; }
            str += Double.toString(Math.round(element * 100.0) / 100.0);
        }
        return str;
    }

    public void dump (Path folder, int index) {
        Path objFile = Paths.get(folder.toString(), Integer.toString(index) + ".obj.txt");
        Path varFile = Paths.get(folder.toString(), Integer.toString(index) + ".var.txt");
        // prepare objectives and variables strings
        ArrayList<String> objStrings = new ArrayList<String>();
        ArrayList<String> varStrings = new ArrayList<String>();
        for (BinarySolution solution: this.solutions) {
            objStrings.add(Result.doubleListToString(solution.getObjectives()));
            List<Boolean> variables = new ArrayList<Boolean>();
            for (BinarySet set: solution.getVariables()) {
                variables.add(set.get(0));
            }
            varStrings.add(Result.booleanListToString(variables));
        }
        // write to file
        try {
            Files.write(objFile, objStrings, StandardCharsets.UTF_8);
        } catch (IOException e) {
            System.out.println("cannot open file: " + objFile.toString());
        }
        try {
            Files.write(varFile, varStrings, StandardCharsets.UTF_8);
        } catch (IOException e) {
            System.out.println("cannot open file: " + varFile.toString());
        }
    }
}
