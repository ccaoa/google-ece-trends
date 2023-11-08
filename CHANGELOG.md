# Google ECE PyTrends Changelog 
[comment]: # (Website for propper changelog documentation: [https://keepachangelog.com/en/0.3.0/])

[Semantic Versioning](https://semver.org/) of the project to track demand for child care across the USA. 

### Unreleased <To become the release notes for the next version>
[//]: # (tagging git releases https://stackoverflow.com/questions/18216991/create-a-tag-in-a-github-repository)
* Create a full summary statistics Excel file from scratch.

## 0.4
**8 Nov 2023**
* Add ability to mathematically summarize pulled data.
* Adds a `dma_id_name_converter()` function to convert DMA ID ~ Name data.
* Move `metadata.xlsx` out of this repository and into the Research Team sharepoint.
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