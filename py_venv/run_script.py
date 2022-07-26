"""
Place this script within a directory in your PYTHON_PATH
And then import it in scripts in your PATH.
Your executable script (test) should look something like this:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#!/usr/bin/env python

from run_script import run_script

run_script("test.py")

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import inspect
import os
import platform
import subprocess
import sys
from pathlib import Path


def run_script(
    script_name: str,
    src_dir: str = "",
    venv_dir: str = "venv",
    level: int = 0,
) -> None:
    """
        Run the python script after activate its virtual environment.
        The virtual environment directory (`venv_dir`) is relative to the script_path.

        Assumes the following structure:

    <root>
    |
    |-- <src>
    |   |-- <script_name>
    |
    |-- venv
    |   |-- bin
    |   |   |-- python

    """

    root_path = Path(inspect.getfile(inspect.currentframe())).parents[level]
    python_path = root_path / venv_dir / "bin" / "python"
    if src_dir:
        script_path = root_path / src_dir / script_name
    else:
        script_path = root_path / script_name

    args = " ".join(sys.argv[1:])

    command = f"{python_path} {script_path} {args}"

    os.environ["ENVPATH"] = str(root_path / ".env")

    try:
        _ = subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as _:  # err:
        pass
