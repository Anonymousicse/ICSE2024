package org.osino.Constraints;

import java.util.HashMap;

public class Optional extends MetaConstraint {
    private String left;
    private String right;

    public Optional(String left, String right) {
        this.left = left;
        this.right = right;
    }

    public String getLeft() {
        return left;
    }

    public void setLeft(String left) {
        this.left = left;
    }

    public String getRight() {
        return right;
    }

    public void setRight(String right) {
        this.right = right;
    }

    @Override
    public boolean evaluate(HashMap<String, Boolean> values) {
        return (!values.get(this.left)) || values.get(this.right);
    }

    @Override
    public String getSense() {
        return "=>";
    }

    @Override
    public String toString() {
        return this.left + " => " + this.right;
    }
}
