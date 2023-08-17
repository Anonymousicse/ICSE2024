from os import path
from pathlib import Path

# Project Root Path
ROOT_DIR = path.dirname(Path(__file__).parent.parent)

# Result Root Path
RESULT_ROOT = path.join(ROOT_DIR, 'result')

# Lib Path
LIB_DIR = path.join(ROOT_DIR, 'lib')

# Dump Path
DUMP_DIR = path.join(ROOT_DIR, 'dump')

# Solver Path
SOLVER_DIR = path.join(ROOT_DIR, 'nen')

# float precision
FLOAT_PRECISION = 1e-6
