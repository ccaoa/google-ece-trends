# Setup python virtual environments for Windows

<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

## Requirements

Ensure the base python interpreter path designated in `set_python_path.bat`
is set to your desired python.exe.

- Package dependencies may require a minimum python version. 
Tip: use the latest version of python you have available. 
- To utilize ESRI's ArcGIS spatial package, `arcpy`, in a venv,
set the python 3 interpreter that comes with the ArcGIS Pro software as your base interpreter.

## Usage
**To simply set up the venv itself, just execute the `setup.bat` file.** That's it.

## Notes
- Conda environments may experience issues installing with `ssl` DLL issues.
- To see more about this workflow, please check out [this repository](https://github.com/cooperjaXC/windows_python_venv).
