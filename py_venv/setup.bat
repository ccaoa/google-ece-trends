:: Establish your local root python path.
:: Set the default for this to be the directory this .bat file is housed within.
set "VENV_DIR=%~dp0"
:: The `@` symbol at the beginning of a command in a batch file is used to prevent the command line from being echoed (displayed) in the console.
:: :: It does not affect the execution of the command itself.
@call "%VENV_DIR%\set_python_path.bat"
:: Set up the virtual environment using the base interpreter.
@%PYTHON_PATH% "%VENV_DIR%\setup.py"
