package org.osino.Constraints;

import java.util.HashMap;
import java.util.ArrayList;

public class AltSubfeatures extends MetaConstraint {
    private ArrayList<String> left;
    private String right;

    public AltSubfeatures(ArrayList<String> left, String right) {
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
        int count = 0;
        if (values.get(this.right)) {
            for (String var: this.left) {
                if (values.get(var)) {
                    count += 1;
                    if (count > 1) {
                        return false;
                    }
                }
            }
            return (count == 1);
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
        return "alt";
    }

    @Override
    public String toString() {
        return this.left.toString() + " alt " + this.right;
    }
}
