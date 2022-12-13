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
# FUNCTION-IZE AT END FOR MORE ROBUST CODE. # We don't want file paths in these "modules" but in data pull .py files.
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

# #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
# ################################## #


def index_as_first_col(indf, new_col_name):
    """ Set the index of a pandas data frame as its first column with a new arbitrary index."""
    outdf = indf.copy()
    outdf[new_col_name] = outdf.index
    # Set new col name for the former IDX as first column
    cols = outdf.columns.to_list()
    cols = cols[-1:] + cols[:-1]
    outdf = outdf[cols]
    # Reset the index to be numerical.
    outdf = outdf.reset_index(drop=True)
    return outdf


def transpose_df(df, first_col_as_new_col_names=True, old_cols_as_index=True, col_of_oldcolumns_name="old_cols"):
    """ Transpose a dataframe with specific index manipulation to fit this Google Trends project."""
    # If the user wanted the first column of the PD DF to function as the column names
    if core.string_to_bool(first_col_as_new_col_names) is True:
        # The first column of the raw dataset containing UOA identifiers will be set as the column names of the new DF.
        first_col = df.columns[0]
        work_df = df.set_index(first_col).transpose()
    else:
        # The first column of the raw dataset containing UOA identifiers will be set as the first row.
        work_df = df.transpose()
    # At this point, the old column headers are the new index column, with the old first column as the first record.
    # # https://stackoverflow.com/a/36013757/15517267
    if core.string_to_bool(old_cols_as_index) is False:
        # If the user wants the old columns bounced out into the first row:
        old_first_column = work_df.columns.name
        if isinstance(col_of_oldcolumns_name, str) is not True:
            try:
                col_of_oldcolumns_name=str(col_of_oldcolumns_name)
            except:
                col_of_oldcolumns_name = "old_cols"
        work_df = index_as_first_col(work_df, col_of_oldcolumns_name)#old_first_column)
    # Otherwise, the old column names will still be the index of the output DF.
    return work_df


# Goal:
# FIRST: Get a tab in a summary xlsx sheet to have columns with all UOAs (eg states or DMAs, whatever they may be) or
# dates (if a temporal DF) & each row is a *pull date* regardless of geog vs temporal dataset.
# THEN: use the columns to calc in a new, other tab each column's (eg, state, DMA, or date
# (day, week, month, etc whatever the temporal UOA was)) summary stats. Both tabs will have the same column headers.
# The only difference will be the rows: raw data values collected into one sheet or summary stats of that data.
# Similar (but not identical) to the SSM GD6/7s or map notes.

def summary_storage_path(same_as_raw_storage=False, use_parent_dir=False):
    """ Define the local path in which you'll store summary result XLSXs. """
    storage_path = get_storage_path()
    if same_as_raw_storage is True:
        return storage_path
    else:
        parent_dir = os.path.dirname(storage_path)
        if use_parent_dir is True:
            return parent_dir
        else:
            # Default to sibling directory in this case named "summary_data"
            name_sibling_dir="summary_data"
            sibling_dir_path = os.path.join(parent_dir,name_sibling_dir)
            if os.path.exists(sibling_dir_path) is False:
                # Create that sibling dir if it does not exist.
                os.mkdir(sibling_dir_path)
            return sibling_dir_path


def define_target_summary_dataset(raw_data_file):
    """ Use the name of the raw data file to target which summary Xlsx you'll be using. """
    if os.path.exists(raw_data_file) is False:
        raise FileNotFoundError
    dataset_name = Path(raw_data_file).stem
    dataset_name = dataset_name[:dataset_name.rfind("_")]
    # This dataset name will be identical to the summary dataset name
    sumstorpath=summary_storage_path()
    summary_dataset_name = dataset_name+'.xlsx'
    full_summary_file_path = os.path.join(sumstorpath, summary_dataset_name)
    return full_summary_file_path


# def append_raw_data_fromdf(raw_gtrends_data_file):
#     """ Append raw Google Trends data stored as an individual file to a larger summary collection of all data collected
#     for the same given study time period and geography."""


def setup_summary_spreadsheet(raw_gtrends_data_file,force=False):
    """ _ """
    basename = os.path.basename(raw_gtrends_data_file)
    target_summary_dataset = define_target_summary_dataset(raw_gtrends_data_file)
    # Check to see if the file already exists
    exists = False
    if os.path.exists(target_summary_dataset) is True:
        # The document already exists. Be very careful to not destroy your data!
        print("The", basename, 'summary file already exists.')
        if force is True:
            # If you're sure........
            print("  Refreshing the file and building from scratch in", os.path.dirname(target_summary_dataset))
            os.remove(target_summary_dataset)
            exists = False
        else:
            print("  The summary file will not be removed or refreshed.")
            exists = True
            return

    # If the script makes it here, the summary spreadsheet does not yet exit. So create it!
    # # The conditional here may not be necessary
    if exists is False:
        # create the summary spreadsheet from the raw data.
        raw_data_in_df = core.file_to_df(raw_gtrends_data_file)
        # FIRST: We need to setup the raw data records collection sheet. All future raw data will be appended here.
        # All we need are the UOA column (eg, date, dma, state, etc) and the GTIS.
        # # The UOA col will be the first one b/c of data formatting in `pull_data.py`.
        uoa_col = raw_data_in_df.columns[0]
        subset_raw_data = raw_data_in_df[[uoa_col]+['gtis']]
        # Get the data from the input file
        trasnposed_sub_df = transpose_df(subset_raw_data, first_col_as_new_col_names=True)
        # Output the first sheet/tab of the xlsx to = the transposed data & the GTIS.
        core.df_to_file(trasnposed_sub_df,target_summary_dataset,index=False,sheet_xlsx="raw_data_records")
        # SECOND: Setup a second tab/sheet in the xlsx that does mathematical calculations for the raw dataset.
        # After the transpose, the UOA is now the column field. It will become the column field for the summary stats.



def append_raw_data_fromfile(raw_gtrends_data_file):
    """ Append raw Google Trends data stored as an individual file to a larger summary collection of all data collected
    for the same given study time period and geography."""
    # Find the summary dataset which to append the data.
    target_summary_dataset = define_target_summary_dataset(raw_gtrends_data_file)
    if os.path.exists(target_summary_dataset) is False:
        # Do stuff to setup the summary xlsx with the current raw data as its first entry.
        setup_summary_spreadsheet(raw_gtrends_data_file)
    else:
        # Append the data to the stuff that is already there.
        # Get the data from the input file
        in_df = core.file_to_df(raw_gtrends_data_file)
        trnspse_in_df = transpose_df(in_df, first_col_as_new_col_names=True)
        columns_column = trnspse_in_df.columns[0]  # This will allow access to fields like 'gtis'

