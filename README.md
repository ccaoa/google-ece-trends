# Google Trends of Child Care

[//]: # (Embedding badges: https://naereen.github.io/badges/) 
![Generic badge](https://img.shields.io/badge/version-0.5.0-blue.svg)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

This is a repository that utilizes the [unofficial python API for Google Trends](https://github.com/GeneralMills/pytrends) 
to systematically pull Google search intensity data about the topic of "child care" for use as a proxy for ECE demand data.
Code here automates data pulls one might otherwise have to access through [Google's Trends GUI](https://trends.google.com). 

## Concept
CCAoA's Research Team has been collecting Google Trends data on the topic of "child care" since 2021
with the idea that search interest for child care can function as a proxy for child care demand,
a notoriously difficult idea to quantify.

Google Trends data, however, are not straightforward. 
It has numerous quirks, and researchers need to be careful when using Trends data in order to draw proper conclusions from it. 

Importantly, **Google Trends data is a sample from the "true" search interest, 
and the daily fluctuations in the reported values are a form of sampling variability.** 
Therefore, this repository helps a user capture Google's daily samples of its own "true" search interest data,
store it on SharePoint, and calculate summary statistics from all the previously collected data.
The more samples the user captures, the closer the user comes to understanding the "true" search interest on Google for
"child care" from which they can draw inferences about ECE demand patterns. 

This code allows the user to define different historical time periods for which they'd like to study ECE demand,
the desired geography of said demand (e.g., the United States, a US state, 
a [Designated Media Area](https://www.nielsen.com/dma-regions/) or "media market"),
and the spatial variation across a geographic subunit of the broader geography (e.g., a US state, 
a [media market](https://www.nielsen.com/dma-regions/), a major city).

## Usage
### [`pull_data.py`](pull_data.py)
This file allows for easy and custom pulls of Google Trends data for different times and places.
#### Key functions:
* **`connect_to_gtrends`** - Establishes a connection to Google Trends in a particular language (English default). 
    Importantly defines the `backoff_factor` which helps circumvent Google blockades (i.e., 429 errors) to datasets.
* **`payload_builder`** - The payload is the base parameter set that tells Google the broad picture of what you're trying to research:
    the 'What, Where, & When' of GTrends data pulls. I.e., what you would manually input into [Google's Trends GUI](https://trends.google.com) 
    Reconstruct a payload every time you want to change one of these base parameters.
* **`extract_data_try`** - Extract any Google Trends data you want: any time, any place.
    Returns a pandas DataFrame.
    * Note: You MUST provide a payload into this function.

### [`store_data.py`](store_data.py)
This file allows for easy storage of already pulled Google Trends data.
#### Key functions:
* **`store_data`** - Store trends data in a particular location with specific location and time naming parameters.
    Ensure the output file name includes metadata on the time period of the data, date of data pull, and the dataset's name.
    Data can be stored as `.xlsx` or `.csv` (default).

### [`append.py`](append.py)
This file produces a single dataset that contains all the previously pulled Google Trends data records per area and time of interest unit.
#### Key functions:
* **`append_raw_data_from_files`** - Appends a list of Google trends XLSX datasets into a compiled all-data XLSX 
in preparation for the calculation of summary statistics.
* **`append_all_raw_files`** - Wrapper for `append_raw_data_from_files()` that appends all Google trends XLSX datasets
in a passed directory into a compiled all-data XLSX in preparation for the calculation of summary statistics.

### [`summarize.py`](summarize.py)
This file, using `trend_calculations.py` formulas, produces summary files that calculate statistics from previously pulled Google Trends data.
#### Key functions:
* **`calc_sumstats`** - Calculates the following statistics for the already-stored xlsx GTrends data:
    * Average Interest Score (GTIS)
    * Std Dev
    * Number of observations
    * Standard Error
    * Confidence Interval
    * Coverage Factor
    * Expanded Uncertainty
    * Rebased GTIS
* **`summarize_collected_data`** - Wrapper for `calc_sumstats()` that summarizes appended data 
and writes the results to the summary XLSX.
* **`summarize_collected_data`** - Wrapper for `summarize_collected_data()` that summarizes all already appended data
in a passed directory and writes the results to the summary XLSX.

### [`late2022_datapulls.py`](late2022_datapulls.py)
This file pulls specific pieces of Google Trends ECE data for 23 AOIs in preparation for a publication on this method.
#### Key functions:
* **`full_gtrends_pull`** - Runs only the data pull (without summarization) for the 23 specified datasets.
* **`full_run_gtrends`** - Runs the data pull and summarization for the 23 specified datasets.

#### Other helping files:
* [`datapulls22.bat`](datapulls22.bat) - Windows Batch file wrapper for executing [`late2022_datapulls.py`](late2022_datapulls.py).
* [`schedule_gtrends_daily_run.bat`](schedule_gtrends_daily_run.bat) - Schedules a daily execution of [`datapulls22.bat`](datapulls22.bat) for automatic data pulls on Windos OS. 

# Other
## Acknowledgements
Thanks to Jacob Schneider for his consultation on this work 
and for providing a spatial shapefile for the Designated Market Areas (DMAs) of the USA. 
See more on [his website](https://sites.google.com/view/jacob-schneider/resources).

## Virtual Environments
If you would like to use direct executable modules from this package as scripts, 
you can create a virtual python environment (venv) to ensure no dependency conflicts. 
To do this, this repository includes a tool to aid in setting up the venv on Windows operating systems. 

### Windows `py_venv` Tool
The [`py_venv`](py_venv) subdirectory includes setup files that can create your venv for you. 

To do this, first open the [`.\py_venv\set_python_path.bat`](py_venv/set_python_path.bat) in a text editor.
Set the `PYTHON_PATH` variable to the base interpreter off of which you want the venv to be built.

* Recommended: use your interpreter that was included in your ArcGIS Pro installation. 
This will ensure you will have all geoprocessing functions accessible in your venv.

Then, execute the following in a **Windows command prompt** with the current directory set to the root of this repo:

```
.\py_venv\setup.bat
```

This batch file will install a virtual python environment for you in the [`py_venv` subdirectory](py_venv) 
based on the specifications in the [`.\requirements.in` file](requirements.in). 

The [`.\py_venv\requirements.txt` file](py_venv/requirements.txt) is generated at the time of the venv setup.
It indicates the most recent development environment in which this repository was developed. 
It is a full `pip freeze` of the development environment.
If you have any package dependency issues, you can reference the [`.\py_venv\requirements.txt`](py_venv/requirements.txt)
 file to compare with your current environment. 

Remember to reference the newly created venv as your new python interpreter. 
This will be located at `.\py_venv\venv\Scripts\python.exe`.

To activate the venv directly in the Windows command prompt, enter
```
.\py_venv\venv\Scripts\activate
```

Warning: housing venvs in locations with excessively long paths may cause errors in installing or importing packages.
Make sure to `git clone` the repository into a folder without a long file path.
