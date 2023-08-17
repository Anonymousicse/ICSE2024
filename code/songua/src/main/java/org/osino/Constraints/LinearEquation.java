package org.osino.Constraints;

import java.util.HashMap;

public class LinearEquation extends MetaConstraint {
    private HashMap<String, Double> left;
    private double right;

    public LinearEquation(HashMap<String, Double> left, double right) {
        this.left = left;
        this.right = right;
    }

    public HashMap<String, Double> getLeft() {
        return left;
    }

    public void setLeft(HashMap<String, Double> left) {
        this.left = left;
    }

    public Double getRight() {
        return right;
    }

    public void setRight(double right) {
        this.right = right;
    }

    @Override
    public String getSense() {
        return "=";
    }

    @Override
    public boolean evaluate(HashMap<String, Boolean> values) {
        double leftAcc = 0.;
        for (String key: this.left.keySet()) {
            if (values.get(key)) {
                leftAcc += this.left.get(key);
            }
        }
        return (leftAcc <= (this.right + 1e-9)) && (leftAcc >= (this.right - 1e-9));
    }

    @Override
    public String toString() {
        return this.left.toString() + " = " + Double.toString(this.right);
    }
}
