package org.osino.Constraints;

import java.util.HashMap;
import java.util.ArrayList;

public class OrSubfeatures extends MetaConstraint {
    private ArrayList<String> left;
    private String right;

    public OrSubfeatures(ArrayList<String> left, String right) {
        this.left = left;
        this.right = right;
    }

    public ArrayList<String> getLeft() {
        return left;
    }

    public void setLeft(ArrayList<String> left) {
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
        if (values.get(this.right)) {
            for (String var: this.left) {
                if (values.get(var)) {
                    return true;
                }
            }
            return false;
        } else {
            for (String var: this.left) {
                if (values.get(var)) {
                    return false;
                }
            }
            return true;
        }
    }

    @Override
    public String getSense() {
        return "or";
    }

    @Override
    public String toString() {
        return this.left.toString() + " or " + this.right;
    }

    
}
