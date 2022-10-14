# Google Trends of Child Care
This is a repository that utilizes the [unofficial python API for Google Trends](https://github.com/GeneralMills/pytrends) 
to systematically pull Google search intensity data about the topic of "child care" for use as a proxy for ECE demand data.
Code here automates data pulls one might otherwise have to access through [Google's Trends GUI](https://trends.google.com). 

## Usage
### `pull_data.py`
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
### `store_data.py`
This file allows for easy storage of already pulled Google Trends data.
#### Key functions:
* **`store_data`** - Store trends data in a particular location with specific location and time naming parameters.
    Ensure the output file name includes metadata on the time period of the data, date of data pull, and the dataset's name.
    Data can be stored as `.xlsx` or `.csv` (default).

# Acknowledgements
Thanks to Jacob Schneider for his consultation on this work 
and for providing a spatial shapefile for the Designated Market Areas (DMAs) of the USA. 
See more on [his website](https://sites.google.com/view/jacob-schneider/resources).
