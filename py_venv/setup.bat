:: Set your root directory that houses your virtual environment content.
::@set VENV_DIR=.
:: Or, set the default directory to be the path where this .bat file is located.
@set VENV_DIR=%~dp0
@call %VENV_DIR%\set_python_path.bat
:: Set up the virtual environment using the base interpreter.
@%PYTHON_PATH% %VENV_DIR%\setup.py
