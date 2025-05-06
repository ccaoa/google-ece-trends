# Google ECE PyTrends Changelog 
[comment]: # (Website for propper changelog documentation: [https://keepachangelog.com/en/0.3.0/])

[Semantic Versioning](https://semver.org/) of the project to track demand for child care across the USA. 

### Unreleased <To become the release notes for the next version>
[//]: # (tagging git releases https://stackoverflow.com/questions/18216991/create-a-tag-in-a-github-repository)
* *No future enhancements are planned. Successful and consistent execution of `v0.5` will yield the release of `v1.0`.*

## 1.0
**4 Oct 2024**
* Add ability to append & summarize custom dates' raw data in the [`datapulls.py`](late2022_datapulls.py).
* Remove Top and Related Queries pulls in 2022 data pulls because of [`pytrends` Issue #628](https://github.com/GeneralMills/pytrends/issues/628#issuecomment-2378810871)
* Add data resulting from 2022-2024 data pulls. This dataset is used in the publication for Cooper et al. (2025).

## 0.5
**5 Jan 2024**
* Separates out the [append](append.py) and [summarize](summarize.py) workflows into two separate scripts
that produce two separate output files in the output directory.
This distinguishes the distinct workflows and nullifies multi-tab output summary XLSX files. 
* Adds a `full_append_and_summary_run()` function in the [summarize](summarize.py) script
to create a full summary statistics Excel file from scratch.
* Enhance and fix bugs in the [2024 paper data collection process](late2022_datapulls.py).
* Upgrade the [virtual environment creation process](py_venv).

## 0.4
**8 Nov 2023**
* Add ability to mathematically summarize pulled data.
* Adds a `dma_id_name_converter()` function to convert DMA ID ~ Name data.
* Sort testing and extra files into the `./extras` subdirectory.

## 0.3
**14 Apr 2023**
* Update the pytrends python requirement to be >=4.9.2 
to account for March 2023 Google updates that caused fails and 
subsequent [pytrends patch](https://github.com/GeneralMills/pytrends/pull/570).
Fixes issue #5.

## 0.2
**26 Oct 2022**
* Add script to systematically handle the storage of pulled trends data.
* Add script to manage the access and use of [Nielsen Designated Market Areas®](https://www.nielsen.com/dma-regions/).
* Add .bat file to automatically run daily pulls of ECE GTrends data.
* Add virtual python environment setup capabilities.

## 0.1
**23 Sept 2022** - *Initial Internal Release* 
* Pull Google Trends data for Child Care.
* Establish framework for mathematically calculating data's summary trends.