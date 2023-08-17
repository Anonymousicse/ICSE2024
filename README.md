There are three folders: data, code and result.

## data

All the data required for the experiment are stored in the **data** folder, and all data sets are stored in the form of *.json* files.

## code

The **code** folder stores all the source code of this experiment. In the folder, there are three folders: experiment, nen, lib and songua.

The **experiment** folder stores the implementation code of three RQs. The execution of RQs depends on the implementation of the algorithm in the nen folder.

The **nen** folder stores the implementation code of MOQA, CQHA, epsilon-constraint algorithm.
/code/nen/Solver/MOQASolver.py provides a python implementation of the MOQA algorithm,
/code/nen/Solver/HybridSolver.py provides a python implementation of the CQHA algorithm,
/code/nen/Solver/ExactECSSolver.py provides a python implementation of the epsilon-constraint algorithm.

The **songua** folder stores the Java version implementation of NSGA-II, and the implementation of NSGA-II depends on the *Jmetal* library.
/code/songua/src/main/java/org/osino/Runners/NSGAII.java provides a Java implementation of the NSGA-II algorithm.
The NSGAII.java is packaged into an *NSGAII.jar* file for calling, it is stored in /code/lib/NSGAII.jar.

The above four files are the core code of this paper.

## result

The **result** folder stores the execution results of three RQs, which are stored in *.csv* files.


## RQ execution steps

The execution code of RQ is mainly in the folder /code/experiment

For RQ1, first run the file /code/experiment/RQ1/epsilon-constraint.py, it will call the /code/nen/Solver/ExactECSSolver.py to solve NRP and FSP using epsilon-constraint algorithm.
Then run the file /code/experiment/RQ1/moqa.py to call the /code/nen/Solver/MOQASolver.py to solve problems using MOQA algorithm
run the file /code/experiment/RQ1/nsgaii.py will call the /code/lib/NSGAII.jar to solve problems using NSGA-II algorithm.
Last, run the /code/experiment/RQ1/RQ1.py to compare the results and calculate the IGD, HV and SP indicators.

For RQ2, first run the files in the path /code/experiment/RQ2/hybrid_moo.py to call /code/nen/Solver/HybridSolver.py to get the calculation results of CQHA. 
Then run the files in the path /code/experiment/RQ2/sngaii_large.py to call the /code/lib/NSGAII.jar to get the calculation results of NSGA-II.
Last, run the RQ2.py in the path /code/experiment/RQ2/RQ2.py to compare the results of CQHA and NSGA-II (calculate the IGD, HV and SP indicators).

For RQ3, first run the files in the path /code/experiment/RQ3/Hybrid_scale.py to call /code/nen/Solver/HybridSolver.py to get the calculation results of CQHA with different parameter *rate*. 
Then, run the RQ3.py in the path /code/experiment/RQ3/RQ3.py to compare the results of CQHA with different parameter *rate* (calculate the IGD, HV and SP indicators).
