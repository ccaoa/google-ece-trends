rem Make sure you set your base python interpreter path in the py_venv\set_python_path.bat file if it's different than the one below.
:: Base python interpreter downloads
::@set PYTHON_PATH="%USERPROFILE%\AppData\Local\Programs\Python\Python310\python.exe"
::@set PYTHON_PATH="%USERPROFILE%\AppData\Local\Programs\Python\Python37\python.exe"
:: Or, dynamically set the python path for base downloaded python interpreters
::: Just set which version of python you're using
@set "PYTHON_VERSION=3.7"
::@set "PYTHON_VERSION=3.10"
::@set PYTHON_PATH="%USERPROFILE%\AppData\Local\Programs\Python\Python%PYTHON_VERSION:.=%\python.exe"
@set PYTHON_PATH="C:\Program Files\Python%PYTHON_VERSION:.=%\python.exe"
::
:: ArcGIS python path
::: If you have recently updated your ArcGIS Pro and subsequently your python interpreter,
::: you may need to follow these steps if you encounter an `ensurepip` error:
::: https://stackoverflow.com/questions/71395733/python-package-creation-on-windows-fails-with-python-exe-im-ensurepip/72192474#72192474
::@set PYTHON_PATH="%ProgramFiles%\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
::@set PYTHON_PATH="%USERPROFILE%\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
::
:: Anaconda Python path
:: @set PYTHON_PATH="%USERPROFILE%\Anaconda3\python.exe"
::
echo %PYTHON_PATH%