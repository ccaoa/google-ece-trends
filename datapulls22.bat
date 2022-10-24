:: PURPOSE: Automate runs of the `late2022_datapulls.py` file.
:: --------------------------------------------------
:: TESTING
::  https://serverfault.com/questions/95686/change-current-directory-to-the-batch-file-directory
:: To ID the current project directory:
::cd %~dp0
:: To ID the venv from the current project directory:
::echo "%~dp0py_venv\venv\Scripts\python.exe"
:: --------------------------------------------------
:: EXECUTION
:: There are two ways of executing this batch file from the cmd shell.
::  Each depends on accessing the file and directory paths correctly.
::
:: 1) Change the working path location to be the same directory as the py_venv subdirectory.
::cd %~dp0
:: Then execute the file.
::@py_venv\venv\Scripts\python.exe .\late2022_datapulls.py
::
:: 2) Access each file relatively without changing directories.
@"%~dp0py_venv\venv\Scripts\python.exe" "%~dp0late2022_datapulls.py"
