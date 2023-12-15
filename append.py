"""
Goal: Produce an append xlsx sheet with columns with all UOAs (eg states or DMAs, whatever they may be) or
dates (if a temporal DF) & each row is a *pull date* regardless of geog vs temporal dataset.
"""

import os, datetime as dt, numpy as np, pandas as pd
from pathlib import Path
# from scipy import stats
from ccaoa import core, raccoon as rc

try:
    from . import dma, pull_data as pull, store_data as store, trend_calculations as tcalc
except ImportError:
    import dma, pull_data as pull, store_data as store, trend_calculations as tcalc

raw_data_collection_file_flag = "raw_data_records"
date_of_pull_field = "pull_date"
gtis_average_field = "gtis_mean"


def summary_storage_path(same_as_raw_storage=False, use_parent_dir=False):
    """ Define the local path in which you'll store summary result XLSXs. """
    storage_path = store.get_storage_path()
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


def transpose_df(df, first_col_as_new_col_names=True, old_cols_as_index=True, col_of_oldcolumns_name="old_cols"):
    """ Transpose a dataframe with specific index manipulation to fit this Google Trends project."""
    # TODO: Migrate this function to a more generalizable format in ccaoa.raccoon module. Then call it here.
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
        work_df = rc.index_to_first_column(work_df, col_of_oldcolumns_name)#old_first_column)
    # Otherwise, the old column names will still be the index of the output DF.
    return work_df


def define_target_append_dataset(raw_data_file: str, out_file_flag: str = raw_data_collection_file_flag) -> str:
    """ Use the name of the raw data file to target which summary Xlsx you'll be using. """
    if os.path.exists(raw_data_file) is False:
        raise FileNotFoundError(raw_data_file)
    dataset_name = Path(raw_data_file).stem
    dataset_name = dataset_name[:dataset_name.rfind("_")]
    sumstorpath = summary_storage_path()
    out_file_flag = str(out_file_flag if out_file_flag.startswith('_') else '_' + out_file_flag)
    summary_dataset_name = dataset_name + out_file_flag + '.xlsx'
    full_summary_file_path = os.path.join(sumstorpath, summary_dataset_name)
    return full_summary_file_path


def setup_append_spreadsheet(raw_gtrends_data_file,force=False):
    """ First-time setup of data collection and summarizing structure for GTrends data analysis. """
    target_summary_dataset = define_target_append_dataset(raw_gtrends_data_file)
    # Check to see if the file already exists
    exists = False
    if os.path.exists(target_summary_dataset) is True:
        # The document already exists. Be very careful to not destroy your data!
        print("The", os.path.basename(target_summary_dataset), 'summary file already exists.')
        if force is True:
            # If you're sure........
            print("  Refreshing the file and building from scratch in", os.path.dirname(target_summary_dataset))
            os.remove(target_summary_dataset)
            exists = False
        else:
            print("  The summary file will not be removed or refreshed.")
            exists = True

    # If the script makes it here, the summary spreadsheet does not yet exit. So create it!
    # # The conditional here may not be necessary
    if exists is False:
        # Create the summary spreadsheet from the raw data.

        # FIRST: We need to setup the raw data records collection sheet. All future raw data will be appended here.
        # All we need are the UOA column (eg, date, dma, state, etc) and the GTIS.
        # # The UOA col will be the first one b/c of data formatting in `pull_data.py`.
        prepped_raw_data = raw_data_appending_prep(raw_gtrends_data_file)
        # Output the first sheet/tab of the xlsx to = the transposed data & the GTIS.
        rc.df_to_file(prepped_raw_data, target_summary_dataset,index=False,sheet_xlsx=raw_data_collection_sheet)


def raw_data_appending_prep(raw_gtrends_data_file):
    """ Functions common to both first init setup of raw data cumulative collection and appending new raw data."""
    raw_data_in_df = rc.file_to_df(raw_gtrends_data_file)
    # Ensure top and rising Qs "value" columns get renamed to 'gtis' for consistency and downstream functionality.
    # # Will not affect DFs without a "value" column.
    raw_data_in_df=raw_data_in_df.rename(columns={"value": 'gtis'})
    # Get only the UOA & GTIS
    uoa_col = raw_data_in_df.columns[0]
    subset_raw_data = raw_data_in_df[[uoa_col] + ['gtis']]
    # Rename the GTIS column with the date of the data pull.
    # That way, you'll be able to tell which raw dataset the GTIS is coming from.
    date_of_data_pull = os.path.splitext(raw_gtrends_data_file)[0][
                        (os.path.splitext(raw_gtrends_data_file)[0]).rfind("_") + 1:]
    formatted_date_of_pull = dt.datetime.strftime(dt.datetime.strptime(date_of_data_pull, "%Y%m%d"), "%m/%d/%Y")
    subset_raw_data = subset_raw_data.rename(columns={'gtis': formatted_date_of_pull})
    # Pull the date-of-pull into its own column for easy downstream access?
    # Problem is that lots of UOA access is done by
    # Transpose the subset data for format adhearance downstream.
    transposed_sub_df = transpose_df(subset_raw_data, first_col_as_new_col_names=True, old_cols_as_index=False,
                                     col_of_oldcolumns_name=date_of_pull_field)
    return transposed_sub_df


def append_raw_data_fromfile(raw_gtrends_data_file):
    """ Append raw Google Trends data stored as an individual file to a larger summary collection of all data collected
    for the same given study time period and geography."""
    # Find the summary dataset which to append the data.
    target_summary_dataset = define_target_summary_dataset(raw_gtrends_data_file)
    if os.path.exists(target_summary_dataset) is False:
        # Do stuff to setup the summary xlsx with the current raw data as its first entry.
        setup_file = setup_summary_spreadsheet(raw_gtrends_data_file)
        appended_df = rc.file_to_df(setup_file,raw_data_collection_sheet)
    else:
        # Prepare your new raw data
        prepped_raw_data = raw_data_appending_prep(raw_gtrends_data_file)
        try:
            # Append the data to the stuff that is already there.
            # Pull in the existing raw data records
            existing_raw_records = rc.file_to_df(target_summary_dataset, raw_data_collection_sheet)
            # # If using indexes: https://stackoverflow.com/a/34236431/15517267
            # df.loc[["x", "y"]]
            # # https://stackoverflow.com/questions/71545135/how-to-append-rows-with-concat-to-a-pandas-dataframe
            appended_df = pd.concat([existing_raw_records,prepped_raw_data])
            # 0s seem to mean something wonky with the data source has gone on. We don't want those. Null out the 0s.
            appended_df = appended_df.replace(0,np.nan)

            # Sort by date to get the earliest rows on top.
            # # This is sorting 2023 early months over 2022 late months. Need the opposite.
            # # Convert field to datetime
            appended_df[date_of_pull_field] = pd.to_datetime(appended_df[date_of_pull_field], format='%m/%d/%Y')
            # # Sort with the most recently added data on top.
            appended_df = appended_df.sort_values(by=date_of_pull_field, ascending=False)
            # # Re-convert the date field to a favorable text format for output printing.
            appended_df[date_of_pull_field] = appended_df[date_of_pull_field].dt.strftime('%m/%d/%Y')

            # Drop any rows that are complete duplicates.
            # # This should keep rows with the same data collection date as long as the values are different.
            # # This way we could presumably take multiple data measurements on the same day,
            # # # collect different data, and use them all.
            # https://stackoverflow.com/questions/23667369/drop-all-duplicate-rows-across-multiple-columns-in-python-pandas
            appended_df = appended_df.drop_duplicates()
        except ValueError or NameError:
            # While the summary file exists, the raw data tabulation sheet does not.
            # Create it and set this prepped raw data as the first record in the tab.
            # setup_file = setup_summary_spreadsheet(raw_gtrends_data_file)
            appended_df = prepped_raw_data #rc.file_to_df(setup_file, raw_data_collection_sheet)

        # Output this data back into its original tab.
        rc.df_to_file(appended_df,target_summary_dataset,add_to_existing_xlsx=True,sheet_xlsx=raw_data_collection_sheet,overwrite_old_sheet=True)

    return appended_df


def append_raw_files_from_list(raw_files_paths_list: list, suppress_prints=False):
    """Append all the raw target files (passed as an argument via a list item) to the summary sheets.
    Corresponds to Issue #8 in GitHub. """
    # If a summary sheet is not yet set up, it should be created in this process.
    # [agg.append_raw_data_fromfile(tf) for tf in raw_files_paths_list]
    # Could use the above to do this, but use for loop to do some helpful print statements
    # TODO: Develop method where individual data are not repeatedly written to the summary stats xlsx. Instead, store appended DF in-memory, *then* write at the end.
    if core.string_to_bool(suppress_prints) is not True:
        print("Appending raw files.")
    counter = 0
    allfilscnt = len(raw_files_paths_list)
    for tf in raw_files_paths_list:
        append_raw_data_fromfile(tf)
        counter+=1
        if core.string_to_bool(suppress_prints) is not True:
            print(counter,'/',allfilscnt,"processed:   ",os.path.basename(tf))
    if core.string_to_bool(suppress_prints) is not True:
        print("---------------------------------------------------------------")


def append_all_raw_files(raw_files_parent_dir: str, suppress_prints=False):
    """ Append the data from all of the raw data files in the directory passed as an argument.
    Corresponds to Issue #8 in GitHub. """
    if os.path.exists(raw_files_parent_dir):
        all_raw_files = [os.path.join(raw_files_parent_dir,rf) for rf in os.listdir(raw_files_parent_dir)]
        append_raw_files_from_list(all_raw_files, suppress_prints=suppress_prints)
        return all_raw_files
    else:
        print("Does not exist as a file directory:",raw_files_parent_dir)
        print("  Try", store.get_storage_path())
        return store.get_storage_path()


if __name__ == '__main__':
    tstfil = r"C:\Users\Jacob.Cooper\NACCRRA\Research Team - Documents\Mapping\google_trends\gtrends_data\raw_data\eugene_time_20200214-20210214_20231214.csv"
    print(define_target_append_dataset(tstfil))
