package org.osino.Constraints;

import java.util.HashMap;

public abstract class MetaConstraint {
    public abstract String toString();
    public abstract String getSense();
    public abstract boolean evaluate(HashMap<String, Boolean> values);
}
