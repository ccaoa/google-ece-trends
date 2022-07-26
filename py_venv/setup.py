#!/usr/bin/env python

"""
\b
Virtual Environment Management utility
    venv clean
    venv setup
    venv [venv]
 
\b
TODO:
    Add global config
    Build initial README.md
    Display password hint
"""

# https://python-packaging.readthedocs.io/en/latest/index.html
# https://www.geeksforgeeks.org/command-line-scripts-python-packaging
# https://pythonhosted.org/an_example_pypi_project/setuptools.html
# https://packaging.python.org/tutorials/packaging-projects

import platform
from pathlib import Path
from shutil import rmtree
import subprocess
from sys import executable


VENV_PATH = Path("./venv")
PYTHON = "python"


'''
def setup(package_name: str) -> None:
    """
    Setup package (venv, setup.py, git, tests)
 
    Assumes directory structure:
      <PACKAGE>
      |-- <PACKAGE>/
          |-- __init__.py
      |-- tests/
          |-- __init__.py
      |-- README.md
      |-- LICENSE
      |-- setup.py
      |-- requirements.in
      |-- requirements.txt
      |-- venv/
      |-- .gitignore
      |-- .git/
    """
    # TODO: use LICENSE templates
    # TODO: use README.md templates
 
    path = Path.cwd()
 
    if not (path / ".git").exists():
        run("git init", shell=True, check=True)
    if not (path / ".gitignore").exists():
        write_gitignore()
 
    (path / package_name).mkdir(exist_ok=True)
    (path / package_name / "__init__.py").touch(exist_ok=True)
    (path / "tests").mkdir(exist_ok=True)
    (path / "tests" / "__init__.py").touch(exist_ok=True)
    (path / "README.md").touch(exist_ok=True)
    (path / "LICENSE").touch(exist_ok=True)
    (path / "setup.py").touch(exist_ok=True)
'''


def remove(path: Path) -> None:
    """Remove file or directory specified by path"""
    if path.exists():
        if path.is_dir():
            rmtree(path)
        else:
            path.unlink()


def modified_after(path1: Path, path2: Path) -> bool:
    """Return if path1 has a modify time after path2"""
    if path1.exists():
        return not path2.exists() or path1.stat().st_mtime > path2.stat().st_mtime
    return False


def clean() -> None:
    """Remove temporary files"""

    remove(VENV_PATH)
    remove(Path("build"))
    remove(Path("dist"))
    for path in Path(".").glob("*.egg-info"):
        remove(path)
    for path in Path(".").rglob("__pycache__"):
        remove(path)


def run(command):
    subprocess.run(command, shell=True, check=True)


def activate_command() -> str:
    """Return command to activate virtual environment"""
    if platform.system() == "Windows":
        source = ""
        activate_path = VENV_PATH / "Scripts/activate.bat"
        separator = " & "
    else:
        source = ". "
        activate_path = VENV_PATH / "bin/activate"
        separator = "; "

    return f"{source}{activate_path}{separator}"


def python_interpreter_path() -> str:
    """Return the path of current python interpreter"""
    return str(executable)


def main() -> None:
    """
    Make virtual environment

    Create requirements.in if it doesn't exist.
    Clean venv if requirements.in was modified after venv.
    Create venv if it doesn't exist.
    Upgrade pip, setuptools and wheel
    Install modules in requirements.in
    Write installed modules to requirements.txt
    """
    requirements_in_path = Path("./requirements.in")
    requirements_txt_path = Path("./requirements.txt")

    if not requirements_in_path.exists():
        requirements_in_path.touch()
    elif modified_after(requirements_in_path, VENV_PATH):
        clean()
    else:
        return

    activate = activate_command()

    PYTHON = python_interpreter_path()

    # run(f"{PYTHON} -m venv {VENV_PATH}")
    run(f'"{PYTHON}" -m venv {VENV_PATH}')
    run(f"{activate} python -m pip install --upgrade pip setuptools wheel pip-tools")
    run(f"{activate} python -m pip install -r {requirements_in_path}")
    run(f"{activate} python -m pip freeze > {requirements_txt_path}")
    # run(f"{activate} pip-compile {requirements_in_path} -o {requirements_txt_path}")
    # run(f"{activate} python -m pip install -r {requirements_txt_path}")
    print("Venv setup executed.")


if __name__ == "__main__":
    main()
