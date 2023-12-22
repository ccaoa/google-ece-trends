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
import ensurepip

# Use __file__ if it's defined, otherwise default to the current working directory
py_venv_dir = Path(__file__).parent if '__file__' in locals() else Path('.')
# Construct the path to the 'venv' directory relative to the script's location
VENV_PATH = py_venv_dir / "venv"
VENV_PATH = VENV_PATH.resolve()
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
        activate_path = f'"{VENV_PATH / "Scripts/activate.bat"}"'
        separator = " & "
    else:
        source = ". "
        activate_path = f'. "{VENV_PATH / "bin/activate"}"'
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
    # 1) Establish paths
    # ROOT; This is this code and the venv's home directory. often named `py_venv`
    # Defined as variable `py_venv_dir` above
    # PARENT DIR; This is the directory where the py_venv code is housed.
    parent_dir = py_venv_dir.parent

    # REQUIREMENTS.IN; what are your base project requirements?
    # The requirements.in file defaults to being located outside the "./py_venv" directory.
    # # This is so that the user can define the requirements at the project-level directory.
    requirements_in_path = parent_dir / "requirements.in"  # Path("./requirements.in")
    # Search for existing instances of `requirements.in`
    # Search first in the Parent directory
    if not requirements_in_path.exists():
        # Search in the other directory for it.
        if (py_venv_dir / "requirements.in").exists():
            requirements_in_path = py_venv_dir / "requirements.in"
    if not requirements_in_path.exists():
        # If the requirements_in_path still does not exist,
        # # point the target directory of the requirements.in file back to the parent (or root) directory.
        requirements_in_path = parent_dir / "requirements.in"
        # Since the file exists in neither location, create an empty requirements file in the root directory.
        requirements_in_path.touch()
    elif modified_after(requirements_in_path, VENV_PATH):
        # If the requirements.in file exists in either target location
        # # and has been edited since this venv creation script last ran *or* is new,
        # create / update the venv.
        clean()
    else:
        # If the requirements.in file exists and has not been edited since this venv creation script last ran, pass.
        print("No changes to your 'requirements.in' file.\nYour venv is up to date.")
        return

    # REQUIREMENTS.TXT; what does the carbon copy of your virtual enviropnment look like?
    # The requirements.txt file defaults to being located inside the "./py_venv" directory.
    # # This is so that the user can find the full requirements readout after the venv is created,
    # # but it is not confusingly included at the project-level directory.
    requirements_txt_path = py_venv_dir / "requirements.txt"  # Path("./py_venv/requirements.txt")
    # Search for existing instances of `requirements.txt`
    if not requirements_txt_path.exists():
        # The root directory will become the default location for the requirements.txt whether it exists or not.
        requirements_txt_path = parent_dir / "requirements.txt"

    # PYTHON INTERPRETER
    activate = activate_command()
    PYTHON = python_interpreter_path()

    # 2) Create the VENV
    print(f'Setting up the VENV at "{VENV_PATH}"')
    # https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment
    try:
        command = f'"{PYTHON}" -m venv "{VENV_PATH}"'
        # print(f"\nExecuting venv creation command: {command}")
        run(command)
        # print(f"\nExecuting activate venv command: {activate}\n")
        run(f"{activate} python -m pip install --upgrade pip setuptools wheel pip-tools")
    except subprocess.CalledProcessError:
        # There is an issue establishing the venv.
        # # With ArcGIS Pro base python interpreters, this often has to do with the ensurepip pip wheel.
        # # Follow pieces of https://stackoverflow.com/questions/51720909/how-to-get-python-m-venv-to-directly-install-latest-pip-version/51721906#51721906 to fix.
        print(
            "Exception: Problem creating venv with default settings."
            "\nUse custom workaround."
        )
        run(f'"{PYTHON}" -m venv "{VENV_PATH}" --without-pip')
        whl = next(Path(ensurepip.__path__[0]).glob("_bundled/pip*.whl"))
        # # Could also be
        # whl = list(Path(ensurepip.__path__[0]).glob("_bundled/pip*.whl"))[0]
        print("Your pip wheel file to use:", whl)
        # All variables set; moving on to executing venv pip install.
        run(
            f'{activate} python "{whl}"/pip install --upgrade pip setuptools wheel pip-tools'
        )
    # print("Made it to the Activate stage")
    pip_install_command = f"{activate}python -m pip install -r \"{requirements_in_path}\""
    print(f"\nExecuting pip install command: {pip_install_command}\n")
    run(pip_install_command)
    run(f'{activate} python -m pip freeze > "{requirements_txt_path}"')
    # run(f"{activate} pip-compile {requirements_in_path} -o {requirements_txt_path}")
    # run(f"{activate} python -m pip install -r {requirements_txt_path}")
    print("Venv setup executed.")


if __name__ == "__main__":
    main()
