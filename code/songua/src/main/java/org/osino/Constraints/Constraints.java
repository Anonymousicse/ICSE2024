package org.osino.Constraints;

import java.util.ArrayList;
import java.util.HashMap;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.TypeReference;

public class Constraints {
    ArrayList<MetaConstraint> constraintList;

    public Constraints() {
        this.constraintList = new ArrayList<MetaConstraint>();
    }

    public ArrayList<MetaConstraint> getConstraintList() {
        return constraintList;
    }

    public void setConstraintList(ArrayList<MetaConstraint> constraintList) {
        this.constraintList = constraintList;
    }

    public int size() {
        return this.constraintList.size();
    }

    public MetaConstraint get(int index) {
        return this.constraintList.get(index);
    }

    public void add (MetaConstraint constraint) {
        constraintList.add(constraint);
    }

    public void add (String leftString, String sense, String rightString) {
        switch (sense) {
            case "<=": {
                HashMap<String, Double> left = JSON.parseObject(leftString, new TypeReference<HashMap<String, Double>>(){});
                double right = JSON.parseObject(rightString, Double.class);
                this.add(new LinearInequation(left, right));
                break;
            }
            case "=": {
                HashMap<String, Double> left = JSON.parseObject(leftString, new TypeReference<HashMap<String, Double>>(){});
                double right = JSON.parseObject(rightString, Double.class);
                this.add(new LinearEquation(left, right));
                break;
            }
            case "<=>": {
                this.add(new Mandatory(leftString, rightString));
                break;
            }
            case "=>": {
                this.add(new Optional(leftString, rightString));
                break;
            }
            case "><": {
                this.add(new Exclude(leftString, rightString));
                break;
            }
            case "or": {
                ArrayList<String> left = JSON.parseObject(leftString, new TypeReference<ArrayList<String>>(){});
                this.add(new OrSubfeatures(left, rightString));
                break;
            }
            case "alt": {
                ArrayList<String> left = JSON.parseObject(leftString, new TypeReference<ArrayList<String>>(){});
                this.add(new AltSubfeatures(left, rightString));
                break;
            }
            default: assert false;
        }
    }
}
