"""Dependency installation logic."""


import sys
import os
import subprocess


class RequirementsInstallException(Exception):
    """Requirements installation exception."""

    pass


class SetupPyInstallException(Exception):
    """Setup.py installation exception."""

    pass


def install_requirements_txt(requirements_txt_location: str) -> None:
    """Install requirements from a requirements.txt file."""
    # see https://pip.pypa.io/en/latest/user_guide/#using-pip-from-your-program
    # need to do sys call
    if not requirements_txt_location.endswith("requirements.txt"):
        raise RequirementsInstallException(
            f"{requirements_txt_location} - should contain a requirements.txt reference"
        )

    cmd = f"{sys.executable} -m pip install -r {requirements_txt_location}"
    print("##")
    print(cmd)
    c = execute_cmd(cmd)
    if c != 0:
        raise RequirementsInstallException(requirements_txt_location)


def install_setup_py(setup_py_location: str) -> None:
    """Install requirements from a setup.py file."""
    # see https://pip.pypa.io/en/latest/user_guide/#using-pip-from-your-program
    # need to do sys call
    if not setup_py_location.endswith("setup.py"):
        raise SetupPyInstallException(
            f"{setup_py_location} - should contain a setup.py reference"
        )

    setup_py_dir_location = os.path.dirname(setup_py_location)

    cmd = f"{sys.executable} -m pip install {setup_py_dir_location}"

    c = execute_cmd(cmd)
    if c != 0:
        raise SetupPyInstallException(setup_py_location)


def execute_cmd(cmd: str, wd: str = None) -> int:
    """Execute a shell command."""
    # we call it like this because the normal exception
    # subprocess.CalledProcessError doesnt return the stderr
    # of the pip call itself (it just says it fails)
    # so we solve it with popen and pipe/capture the output
    p = subprocess.run(cmd, shell=True, cwd=wd)
    # output, error = p.communicate()
    return p.returncode
    if p.returncode != 0:
        raise Exception(f"cmd '{cmd}' statuscode: {p.returncode}")
