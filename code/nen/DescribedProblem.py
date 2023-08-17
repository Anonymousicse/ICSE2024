from typing import List, Dict, Any
from os import path
import json
from nen.util.util import ROOT_DIR


class DescribedProblem:
    """ [summary] Define the structure of problems in data which could loaded directly in this project.
    """
    # configs
    DATA_PATH = path.join(ROOT_DIR, 'data')
    RAW_DATA_PATH = path.join(DATA_PATH, 'raw')

    def __init__(self) -> None:
        """__init__ [summary] variables is a list of variables names;
        objectives is a dict mapping objective name to a dict, which maps variables names to their coefs;
            (all objectives are being minimized)
        constraints is a list of constraint list, one constraint list is composed by three part:
            left, sense and right, left may be a list of a dict,
            sense is a str which denotes the constraint type,
            right may be a str or num(float).
        """
        self.variables: List[str] = []
        self.objectives: Dict[str, Dict[str, float]] = {}
        self.constraints: List[List[Any]] = []

    def check(self) -> None:
        """check [summary] check self if is legal, use assertions
        checklist: (empty)
        """
        pass

    def dump(self, file_name: str) -> None:
        """dump [summary] dump self to a json file
        Args:
            file_name (str): [description] name of file constains certain problem
        """
        file_name = path.join(DescribedProblem.DATA_PATH, file_name + '.json')
        content = {'variables': self.variables, 'objectives': self.objectives, 'constraints': self.constraints}
        try:
            with open(file_name, 'w+') as file_out:
                json.dump(content, file_out, indent=2)
                file_out.close()
        except IOError:
            assert False, 'cannot find file:\n\t{}'.format(path.abspath(file_name))

    def load(self, file_name: str) -> None:
        """load [summary] load described problem from certain json file
        Args:
            file_name (str): [description] name of file constains certain problem
        """
        file_name = path.join(DescribedProblem.DATA_PATH, file_name + '.json')
        content: Dict[str, Any] = {}
        try:
            with open(file_name, 'r+') as file_in:
                content = json.load(file_in)
                assert 'variables' in content
                assert 'objectives' in content
                assert 'constraints' in content
                self.variables = content['variables']
                self.objectives = content['objectives']
                self.constraints = content['constraints']
                file_in.close()
        except IOError:
            assert False, 'cannot find file:\n\t{}'.format(path.abspath(file_name))
