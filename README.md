# Google Trends of Child Care

[//]: # (Embedding badges: https://naereen.github.io/badges/) 
[![Version](https://img.shields.io/badge/version-1.0.0-1C3563.svg)](https://github.com/ccaoa/google-ece-trends)
[![Python versions](https://img.shields.io/badge/python-3.7-E6BD29.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://black.readthedocs.io/)
---
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

# Data
Data were systematically collected with identical query parameters using code from this repository.
We collected over 400 replicate data extracts for each of 19 different identical query parameter sets
 from 9 October 2022 to 3 October 2024.
These query parameters can be found in the table below and correspond to commands in [the data pulls script](late2022_datapulls.py).

| Area of Interest (AOI) | AOI Level | Data Type | Sub-unit | Start: search period | End: search period | n(Samples pulled) |
|------------------------|-----------|-----------|----------|----------------------|--------------------|-------------------|
| United States          | Country   | Spatial   | States   | 3 Jun 2018           | 10 Sept 2022       | 429               |
| United States          | Country   | Spatial   | DMAs     | 3 Jun 2018           | 10 Sept 2022       | 405               |
| United States          | Country   | Temporal  | Week     | 3 Jun 2018           | 10 Sept 2022       | 402               |
| Kentucky               | State     | Spatial   | DMAs     | 3 Jun 2018           | 10 Sept 2022       | 405               |
| Indiana                | State     | Spatial   | DMAs     | 3 Jun 2018           | 10 Sept 2022       | 402               |
| Ohio                   | State     | Spatial   | DMAs     | 3 Jun 2018           | 10 Sept 2022       | 408               |
| Kentucky               | State     | Temporal  | Week     | 3 Jun 2018           | 10 Sept 2022       | 406               |
| Indiana                | State     | Temporal  | Week     | 3 Jun 2018           | 10 Sept 2022       | 399               |
| Ohio                   | State     | Temporal  | Week     | 3 Jun 2018           | 10 Sept 2022       | 404               |
| United States          | Country   | Spatial   | States   | 14 Feb 2020          | 14 Feb 2021        | 433               |
| United States          | Country   | Spatial   | DMAs     | 14 Feb 2020          | 14 Feb 2021        | 409               |
| United States          | Country   | Temporal  | Week     | 14 Feb 2020          | 14 Feb 2021        | 397               |
| Minnesota              | State     | Temporal  | Week     | 14 Feb 2020          | 14 Feb 2021        | 419               |
| Oregon                 | State     | Temporal  | Week     | 14 Feb 2020          | 14 Feb 2021        | 417               |
| Minnesota              | State     | Spatial   | DMAs     | 14 Feb 2020          | 14 Feb 2021        | 404               |
| Oregon                 | State     | Spatial   | DMAs     | 14 Feb 2020          | 14 Feb 2021        | 396               |
| Eugene, OR             | DMA       | Temporal  | Week     | 14 Feb 2020          | 14 Feb 2021        | 422               |
| Texas                  | State     | Spatial   | DMA      | 21 Mar 2021          | 21 Apr 2021        | 380               |
| Texas                  | State     | Temporal  | Day      | 21 Mar 2021          | 21 Apr 2021        | 381               |

# Other
## Acknowledgements
Thanks to Jacob Schneider for his consultation on this work 
and for providing a spatial shapefile for the Designated Market Areas (DMAs) of the USA. 
See more on [his website](https://sites.google.com/view/jacob-schneider/resources).

## Virtual Environments
If you would like to use direct executable modules from this package as scripts, 
you can create a virtual python environment (venv) to ensure no dependency conflicts. 
To do this, execute the following in a command prompt (e.g., WSL)
```bash
python -m venv venv
```

Then, referencing your new interpreter, install the packages specified in the [`.\requirements.in` file](requirements.in). 

```bash
.\venv\Scripts\python.exe -m pip install -r requirements.in
```

The [`.\requirements.txt` file](requirements.txt) is a full `pip freeze` of the development environment.
It indicates the most recent development environment in which this repository was developed. 
If you have any package dependency issues, you can reference the [`.\requirements.txt` file](requirements.txt)
 to compare with your current environment. 
