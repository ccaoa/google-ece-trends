"""
lskdjf
"""

import os, datetime as dt, pandas as pd
from ccaoa import core
# from time import time, sleep
from pathlib import Path

try:
    from . import pull_data as pull, store_data as store, dma, trend_calculations as tcalc
except ImportError:
    import pull_data as pull, store_data as store, dma, trend_calculations as tcalc


# Need to Transpose the individual data pull records, append them to the master pull list, and recalc the sum stats.
# May be somewhat similar to Graph Data 6, but output multiple tabs in 1 XLSX:
# * GD6-esque record-level list (from which the sum stats will be calculated)
# * Sum Stats (top 3 lines from the old GTrends xlsxs) with every var re-transposed to be the record and their
#   * Average
#   * Std Dev
#   * N
#   * Coverage Factor
#   * Expanded Uncertainty


# ################################## #
# #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
# ONLY FOR TESTING PURPOSES!
# FUNCTION-IZE AT END FOR MORE ROBUST CODE.
def get_storage_path():
    """Dynamically define the storage path with an external file that you gitignore.
    Keeps one from having to constantly edit their file paths in-code if working on different machines."""
    current_directory = dma.dma_module_directory()
    dot_storage_path = os.path.join(current_directory, ".storage_path")
    if not os.path.exists(dot_storage_path):
        Path(dot_storage_path).touch()
    with open(dot_storage_path) as sfile:
        path_store = str(sfile.read())
    # Make sure there are no pythonic quotations, etc around the path.
    path_store = path_store.replace('r"', '"').replace('"', "")
    if not os.path.exists(path_store):
        print(
            "Your file",
            path_store,
            "doesn't exist.\n"
            "Edit your `.storage_path` file in this directory to designate a destination for the Google Trends data.",
        )
        # # Maybe in a future version, add a user input method to manually define this var in-run.
    sfile.close()
    return path_store
storage_path = get_storage_path()
# #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
# ################################## #

def transpose_df(df, first_col_as_new_col_names=True):
    """ Transpose a dataframe with specific index manipulation to fit this Google Trends project."""
    df.set_index('dma').transpose()
