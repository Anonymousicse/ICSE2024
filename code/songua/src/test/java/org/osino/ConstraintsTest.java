package org.osino;

import org.junit.Assert;
import org.junit.Test;

import java.util.HashMap;
import java.util.ArrayList;

import org.osino.Constraints.MetaConstraint;
import org.osino.Constraints.LinearInequation;
import org.osino.Constraints.LinearEquation;
import org.osino.Constraints.Optional;
import org.osino.Constraints.Mandatory;
import org.osino.Constraints.Exclude;
import org.osino.Constraints.AltSubfeatures;
import org.osino.Constraints.OrSubfeatures;
import org.osino.Constraints.Constraints;

public class ConstraintsTest {
    @Test
    public void testEachConstraint() {
        // linear Poly Constraint
        HashMap<String, Boolean> v0 = new HashMap<String, Boolean>();
        v0.put("x", false); v0.put("y", false); v0.put("z", false);
        HashMap<String, Double> left = new HashMap<String, Double>();
        // Linear Inequation
        left.put("x", 1.0); left.put("y", 2.0); left.put("z", 4.0);
        MetaConstraint inq = new LinearInequation(left, 3.0);
        v0.put("x", false); v0.put("y", false); v0.put("z", false);
        Assert.assertTrue(inq.evaluate(v0));
        v0.put("x", false); v0.put("y", false); v0.put("z", true);
        Assert.assertFalse(inq.evaluate(v0));
        v0.put("x", true); v0.put("y", true); v0.put("z", false);
        Assert.assertTrue(inq.evaluate(v0));
        v0.put("x", false); v0.put("y", true); v0.put("z", true);
        Assert.assertFalse(inq.evaluate(v0));
        v0.put("x", true); v0.put("y", false); v0.put("z", false);
        Assert.assertTrue(inq.evaluate(v0));
        v0.put("x", true); v0.put("y", true); v0.put("z", true);
        Assert.assertFalse(inq.evaluate(v0));
        // Linear Equation
        left.put("x", 1.0); left.put("y", 2.0); left.put("z", 1.0);
        MetaConstraint equ = new LinearEquation(left, 3.0);
        v0.put("x", false); v0.put("y", false); v0.put("z", false);
        Assert.assertFalse(equ.evaluate(v0));
        v0.put("x", true); v0.put("y", false); v0.put("z", true);
        Assert.assertFalse(equ.evaluate(v0));
        v0.put("x", true); v0.put("y", true); v0.put("z", false);
        Assert.assertTrue(equ.evaluate(v0));
        v0.put("x", false); v0.put("y", true); v0.put("z", true);
        Assert.assertTrue(equ.evaluate(v0));
        v0.put("x", true); v0.put("y", false); v0.put("z", false);
        Assert.assertFalse(equ.evaluate(v0));
        v0.put("x", true); v0.put("y", true); v0.put("z", true);
        Assert.assertFalse(equ.evaluate(v0));
        // Bi-Variable Constraints
        HashMap<String, Boolean> v1 = new HashMap<String, Boolean>();
        v1.put("x", false); v1.put("y", false);
        // Optional
        MetaConstraint opt = new Optional("x", "y");
        v1.put("x", false); v1.put("y", false);
        Assert.assertTrue(opt.evaluate(v1));
        v1.put("x", false); v1.put("y", true);
        Assert.assertTrue(opt.evaluate(v1));
        v1.put("x", true); v1.put("y", false);
        Assert.assertFalse(opt.evaluate(v1));
        v1.put("x", true); v1.put("y", true);
        Assert.assertTrue(opt.evaluate(v1));
        // Mandatory
        MetaConstraint man = new Mandatory("x", "y");
        v1.put("x", false); v1.put("y", false);
        Assert.assertTrue(man.evaluate(v1));
        v1.put("x", false); v1.put("y", true);
        Assert.assertFalse(man.evaluate(v1));
        v1.put("x", true); v1.put("y", false);
        Assert.assertFalse(man.evaluate(v1));
        v1.put("x", true); v1.put("y", true);
        Assert.assertTrue(man.evaluate(v1));
        // Exclude
        MetaConstraint exc = new Exclude("x", "y");
        v1.put("x", false); v1.put("y", false);
        Assert.assertTrue(exc.evaluate(v1));
        v1.put("x", false); v1.put("y", true);
        Assert.assertTrue(exc.evaluate(v1));
        v1.put("x", true); v1.put("y", false);
        Assert.assertTrue(exc.evaluate(v1));
        v1.put("x", true); v1.put("y", true);
        Assert.assertFalse(exc.evaluate(v1));
        // Subfeatures
        HashMap<String, Boolean> v2 = new HashMap<String, Boolean>();
        v2.put("x", false); v2.put("y", false); v2.put("z", false); v2.put("f", false);
        ArrayList<String> leftList = new ArrayList<String>();
        leftList.add("x"); leftList.add("y"); leftList.add("z");
        // OrSubfeatures
        MetaConstraint ors = new OrSubfeatures(leftList, "f");
        v2.put("x", false); v2.put("y", false); v2.put("z", false); v2.put("f", false);
        Assert.assertTrue(ors.evaluate(v2));
        v2.put("x", false); v2.put("y", true); v2.put("z", false); v2.put("f", false);
        Assert.assertFalse(ors.evaluate(v2));
        v2.put("x", true); v2.put("y", false); v2.put("z", false); v2.put("f", false);
        Assert.assertFalse(ors.evaluate(v2));
        v2.put("x", false); v2.put("y", false); v2.put("z", false); v2.put("f", true);
        Assert.assertFalse(ors.evaluate(v2));
        v2.put("x", false); v2.put("y", true); v2.put("z", false); v2.put("f", true);
        Assert.assertTrue(ors.evaluate(v2));
        v2.put("x", false); v2.put("y", true); v2.put("z", true); v2.put("f", true);
        Assert.assertTrue(ors.evaluate(v2));
        v2.put("x", true); v2.put("y", false); v2.put("z", false); v2.put("f", true);
        Assert.assertTrue(ors.evaluate(v2));
        v2.put("x", true); v2.put("y", true); v2.put("z", true); v2.put("f", true);
        Assert.assertTrue(ors.evaluate(v2));
        // AltSubfeatures
        MetaConstraint alt = new AltSubfeatures(leftList, "f");
        v2.put("x", false); v2.put("y", false); v2.put("z", false); v2.put("f", false);
        Assert.assertTrue(alt.evaluate(v2));
        v2.put("x", false); v2.put("y", true); v2.put("z", false); v2.put("f", false);
        Assert.assertFalse(alt.evaluate(v2));
        v2.put("x", true); v2.put("y", false); v2.put("z", false); v2.put("f", false);
        Assert.assertFalse(alt.evaluate(v2));
        v2.put("x", false); v2.put("y", false); v2.put("z", false); v2.put("f", true);
        Assert.assertFalse(alt.evaluate(v2));
        v2.put("x", false); v2.put("y", true); v2.put("z", false); v2.put("f", true);
        Assert.assertTrue(alt.evaluate(v2));
        v2.put("x", false); v2.put("y", true); v2.put("z", true); v2.put("f", true);
        Assert.assertFalse(alt.evaluate(v2));
        v2.put("x", true); v2.put("y", false); v2.put("z", false); v2.put("f", true);
        Assert.assertTrue(alt.evaluate(v2));
        v2.put("x", true); v2.put("y", true); v2.put("z", true); v2.put("f", true);
        Assert.assertFalse(alt.evaluate(v2));
    }

    @Test
    public void testConstraints() {
        // add constraint with certain type
        Constraints csts = new Constraints();
        HashMap<String, Double> left = new HashMap<String, Double>();
        left.put("x", 1.0); left.put("y", 2.0); left.put("z", 4.0);
        csts.add(new LinearInequation(left, 3.0));
        csts.add(new LinearEquation(left, 3.0));
        csts.add(new Optional("x", "y"));
        csts.add(new Mandatory("x", "y"));
        csts.add(new Exclude("x", "y"));
        ArrayList<String> leftList = new ArrayList<String>();
        leftList.add("x"); leftList.add("y"); leftList.add("z");
        csts.add(new OrSubfeatures(leftList, "f"));
        csts.add(new AltSubfeatures(leftList, "f"));

        Assert.assertTrue(csts.get(0) instanceof LinearInequation);
        Assert.assertTrue(csts.get(1) instanceof LinearEquation);
        Assert.assertTrue(csts.get(2) instanceof Optional);
        Assert.assertTrue(csts.get(3) instanceof Mandatory);
        Assert.assertTrue(csts.get(4) instanceof Exclude);
        Assert.assertTrue(csts.get(5) instanceof OrSubfeatures);
        Assert.assertTrue(csts.get(6) instanceof AltSubfeatures);

        // add constraint with strings
        csts = new Constraints();
        csts.add("{\"x\": 1.2, \"y\": 0.3, \"z\": 3}", "<=", "3.6");
        csts.add("{\"x\": 1.2, \"y\": 0.3, \"z\": 3}", "=", "3.6");
        csts.add("x", "=>", "y");
        csts.add("x", "<=>", "y");
        csts.add("x", "><", "y");
        csts.add("[\"x\", \"y\", \"z\"]", "or", "f");
        csts.add("[\"x\", \"y\", \"z\"]", "alt", "f");

        Assert.assertTrue(csts.get(0) instanceof LinearInequation);
        Assert.assertTrue(csts.get(1) instanceof LinearEquation);
        Assert.assertTrue(csts.get(2) instanceof Optional);
        Assert.assertTrue(csts.get(3) instanceof Mandatory);
        Assert.assertTrue(csts.get(4) instanceof Exclude);
        Assert.assertTrue(csts.get(5) instanceof OrSubfeatures);
        Assert.assertTrue(csts.get(6) instanceof AltSubfeatures);
    }
}
