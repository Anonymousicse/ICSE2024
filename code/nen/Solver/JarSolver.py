from os import path
from pathlib import Path
import subprocess
import json
from nen.util.util import LIB_DIR, DUMP_DIR


class JarSolver:
    """ [summary] An interface for calling .jar solver
    """
    @staticmethod
    def run_cmd(solver_name: str, config_name: str) -> None:
        """run_cmd [summary] call the solver.jar with config file name (in dump path).
        """
        # check solver file and config file
        assert path.isfile(path.join(LIB_DIR, solver_name + '.jar'))
        assert path.isfile(path.join(DUMP_DIR, config_name + '.json'))
        # prepare cmd
        cmd = 'java -jar {solver_file} {config_file}'
        cmd = cmd.format(solver_file=path.join(LIB_DIR, solver_name + '.jar'),
                         config_file=path.join(DUMP_DIR, config_name + '.json'))
        print('exec> ' + cmd)
        # run in shell
        subprocess.run(cmd, shell=True)
        print('{} process end.'.format(solver_name))

    @staticmethod
    def dump_config(name: str, **args) -> None:
        """
        exec_time:
        limit the NSGA-II running time,
        if <= 0, means no limit.
        """
        file_name = path.join(DUMP_DIR, name + '.json')
        Path(DUMP_DIR).mkdir(parents=False, exist_ok=True)
        content = {}
        for key, value in args.items():
            if len(str(value)) > 512:
                content[key] = '...'
            else:
                content[key] = value
        print(content)
        with open(file_name, 'w+') as json_out:
            json.dump(args, json_out, indent=2)

    @staticmethod
    def solve(solver_name: str, config_name: str, **args) -> None:
        """solve [summary] solve with calling the solver and give some parameters.
        """
        JarSolver.dump_config(config_name, **args)
        JarSolver.run_cmd(solver_name, config_name)
