package org.osino.Results;

import java.util.List;
import java.util.ArrayList;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.io.File;
import java.nio.file.Files;
import java.nio.charset.StandardCharsets;
import java.io.IOException;

import org.uma.jmetal.solution.binarysolution.BinarySolution;
import org.uma.jmetal.util.binarySet.BinarySet;
import com.alibaba.fastjson.JSON;

import org.osino.CBSolution;

public class Results {
    private List<Result> results = new ArrayList<Result>();
    
    public Results () {}

    public void put (Result result) {
        results.add(result);
    }

    private class Info {
        private int iteration;
        private List<Double> elapseds;
        private List<Double> total_num_anneals;

        public Info (int iteration, List<Double> elapseds, List<Double> total_num_anneals) {
            this.iteration = iteration;
            this.elapseds = elapseds;
            this.total_num_anneals = total_num_anneals;
        }
        public int getIteration () { return this.iteration; }
        public List<Double> getElapseds () { return this.elapseds; }
        public List<Double> getTotal_num_anneals() {return this.total_num_anneals; }
    }

    public void dump (Path folder, String methodName) {
        // prepare the dump folder
        new File(folder.toString()).mkdirs();
        int iteration = this.results.size();
        ArrayList<Double> timeList = new ArrayList<Double>();
        for (Result r: this.results) {
            timeList.add(r.getElapsedTime());
        }
        ArrayList<Double> num_anneal = new ArrayList<Double>();
        for (Result r: this.results) {
            num_anneal.add(r.getTotal_num_anneals());
        }
        // dump info json
        Path infoFile = Paths.get(folder.toString(), methodName + ".info.json");
        try {
            ArrayList<String> tmp = new ArrayList<String>();
            tmp.add(JSON.toJSONString(new Info(iteration, timeList, num_anneal)));
            Files.write(infoFile, tmp, StandardCharsets.UTF_8);
        } catch (IOException e) {
            System.out.println("cannot open file: " + infoFile.toString());
        }
        // dump solution list of each result
        for (int index = 0; index < iteration; ++ index) {
            this.results.get(index).dump(folder, index);
        }
    }

    public static BinarySet toBinarySet(boolean value) {
        BinarySet b = new BinarySet(1);
        b.set(0, value);
        return b;
    }

    public static void main(String[] args) {
        Results results = new Results();
        List<BinarySolution> solutions = new ArrayList<BinarySolution>();
        List<Integer> vars = new ArrayList<Integer>();
        vars.add(1); vars.add(1); vars.add(1); vars.add(1); vars.add(1); 
        CBSolution s = new CBSolution(vars, 2, 2);
        BinarySolution s1 = new CBSolution(s);
        BinarySolution s2 = new CBSolution(s);
        BinarySolution s3 = new CBSolution(s);
        BinarySet b = new BinarySet(1);
        // s1: 00101, 1.2, 3.3333
        s1.setVariable(0, toBinarySet(false));
        s1.setVariable(1, toBinarySet(false));
        s1.setVariable(2, toBinarySet(true));
        s1.setVariable(3, toBinarySet(false));
        s1.setVariable(4, toBinarySet(true));
        s1.setObjective(0, 1.2); s1.setObjective(1, 3.33333);
        s1.setConstraint(0, 0.0); s1.setConstraint(0, -1.0);
        // s2: 11001, 0.5, -19.2
        s2.setVariable(0, toBinarySet(true));
        s2.setVariable(1, toBinarySet(true));
        s2.setVariable(2, toBinarySet(false));
        s2.setVariable(3, toBinarySet(false));
        s2.setVariable(4, toBinarySet(true));
        s2.setObjective(0, 0.5); s2.setObjective(1, -19.2);
        s2.setConstraint(0, 0.0); s2.setConstraint(0, 0.0);
        // s3: 01010, 11, 22
        s3.setVariable(0, toBinarySet(false));
        s3.setVariable(1, toBinarySet(true));
        s3.setVariable(2, toBinarySet(false));
        s3.setVariable(3, toBinarySet(true));
        s3.setVariable(4, toBinarySet(false));
        s3.setObjective(0, 11); s3.setObjective(1, 22);
        b.set(0, false); s3.setVariable(4, b);
        s3.setConstraint(0, 0.0); s3.setConstraint(0, 0.0);
        solutions.add(s1); solutions.add(s2); solutions.add(s3); 
        for (int i = 0; i < 5; ++ i) {
            Result result = new Result(i * 0.5, solutions);
            results.put(result);
        }
        results.dump(Paths.get(Paths.get(System.getProperty("user.dir")).toString(), "tmp").toAbsolutePath(), "tmpMethod");
    }
}

