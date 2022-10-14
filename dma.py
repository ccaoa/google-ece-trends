"""
File for handling unique operations pertaining to Neilsen Designated Market Areas used by Google Trends to report
sub-state trends data.
"""

import os, inspect, json

from ccaoa import core


def find_jsons():
    """Find the JSON files that store dictionary items and return a list of the files.
    0) dma_code_dict.json - Sets a unique identifier (key) for all USA DMA regions (value).
    1) state_dma_dict.json - Connects all DMAs (values) associated with (key) state."""
    cur_path = os.path.realpath(
        os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0])
    )
    dma_id_fil = "dma_code_dict.json"
    state_targ_fil = "state_dma_dict.json"
    file_names = [dma_id_fil, state_targ_fil]
    json_directory = os.path.join(cur_path, "json")
    if os.path.exists(json_directory) is False:
        potential_json_dir = [
            root for root, dirs, files in os.walk(cur_path) if dma_id_fil in files
        ][0]
        if os.path.exists(potential_json_dir):
            json_directory = potential_json_dir
            del potential_json_dir
        else:
            print(
                "There was an error finding the JSON dictionary subdirectory.\nFix this issue in a coding bugfix."
            )
            # Basically, figure out a smart exception later. Just get it working now.
            json_directory = None  # This will error below
    # Set the file paths for the GTrends Json files in a list. Access by indexing downstream.
    list_of_json_dicts = [
        os.path.join(json_directory, j)
        for j in file_names
        if os.path.exists(os.path.join(json_directory, j))
    ]
    return list_of_json_dicts


def json_to_python_dict(json_file):
    """Pass a json file and return a python dictionary."""
    # ADD TO CCAOA.CORE - will be added for v2.0 release.
    with open(json_file) as open_the_json:
        python_dict = json.load(open_the_json)
    return python_dict


def dma_id_dict():
    """Returns a dictionary that connects each media market (DMA) to its unique ID."""
    # ID the target ID ~ DMA JSON file
    dma_id_json = find_jsons()[0]
    dma_id_crosswalk = json_to_python_dict(dma_id_json)
    return dma_id_crosswalk


def dmas_all_for_state_dict(state):
    """For state, extract all associated DMAs & their unique IDs."""
    # Use the appropriate json file.
    state_dma_json = find_jsons()[1]
    # Extract the full contents of the JSON into a python dictionary.
    states_dmas_dict = json_to_python_dict(state_dma_json)
    # return states_dmas_dict  # This would've returned the entire json content. We want just 1 state.
    # Format the state argument correctly.
    state = core.st_upperformat(state)
    # Extract just those DMAs associated with <state>.
    targ_state_dma_dict = states_dmas_dict[state]
    # Return a dict of {ID: DMA,} for <state>
    return targ_state_dma_dict
