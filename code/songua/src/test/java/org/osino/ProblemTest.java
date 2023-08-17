package org.osino;

import org.junit.Test;

import java.util.ArrayList;
import java.util.Arrays;

public class ProblemTest {
    @Test
    public void testProblem() {
        ArrayList<String> problems = new ArrayList<String>(Arrays.asList(
            "Drupal", "E-Shop", "make", "ms", "rp", "WebPortal"
        ));
        for (String problemName: problems) {
            new Problem(problemName, new ArrayList<String>());
        }
    }

    public static void main(String[] args) {
        Problem p = new Problem("ms", new ArrayList<String>());
        System.out.println(p);
    }
}
