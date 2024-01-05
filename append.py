"""
Goal: Produce an append xlsx sheet with columns with all UOAs (eg states or DMAs, whatever they may be) or
dates (if a temporal DF) & each row is a *pull date* regardless of geog vs temporal dataset.
"""

import os, datetime as dt, numpy as np, pandas as pd
from pathlib import Path

# from scipy import stats
from ccaoa import core, raccoon as rc

try:
    from . import store_data as store
except ImportError:
    import store_data as store

raw_data_collection_file_flag = "raw_data_records"
date_of_pull_field = "pull_date"
gtis_average_field = "gtis_mean"


def summary_storage_path(same_as_raw_storage=False, use_parent_dir=False):
    """Define the local path in which you'll store summary result XLSXs."""
    storage_path = store.get_storage_path()
    if same_as_raw_storage is True:
        return storage_path
    else:
        parent_dir = os.path.dirname(storage_path)
        if use_parent_dir is True:
            return parent_dir
        else:
            # Default to sibling directory in this case named "summary_data"
            name_sibling_dir = "summary_data"
            sibling_dir_path = os.path.join(parent_dir, name_sibling_dir)
            if os.path.exists(sibling_dir_path) is False:
                # Create that sibling dir if it does not exist.
                os.mkdir(sibling_dir_path)
            return sibling_dir_path


# def transpose_df(df, first_col_as_new_col_names=True, old_cols_as_index=True, col_of_oldcolumns_name="old_cols"):
#     """ Transpose a dataframe with specific index manipulation to fit this Google Trends project."""
#     # If the user wanted the first column of the PD DF to function as the column names
#     if core.string_to_bool(first_col_as_new_col_names) is True:
#         # The first column of the raw dataset containing UOA identifiers will be set as the column names of the new DF.
#         first_col = df.columns[0]
#         work_df = df.set_index(first_col).transpose()
#     else:
#         # The first column of the raw dataset containing UOA identifiers will be set as the first row.
#         work_df = df.transpose()
#     # At this point, the old column headers are the new index column, with the old first column as the first record.
#     # # https://stackoverflow.com/a/36013757/15517267
#     if core.string_to_bool(old_cols_as_index) is False:
#         # If the user wants the old columns bounced out into the first row:
#         old_first_column = work_df.columns.name
#         if isinstance(col_of_oldcolumns_name, str) is not True:
#             try:
#                 col_of_oldcolumns_name=str(col_of_oldcolumns_name)
#             except:
#                 col_of_oldcolumns_name = "old_cols"
#         work_df = rc.index_to_first_column(work_df, col_of_oldcolumns_name)#old_first_column)
#     # Otherwise, the old column names will still be the index of the output DF.
#     return work_df


def define_target_append_dataset(
    raw_data_file: str, out_file_flag: str = raw_data_collection_file_flag
) -> str:
    """Use the name of the raw data file to target which summary Xlsx you'll be using."""
    if os.path.exists(raw_data_file) is False:
        raise FileNotFoundError(raw_data_file)
    dataset_name = Path(raw_data_file).stem
    dataset_name = dataset_name[: dataset_name.rfind("_")]
    sumstorpath = summary_storage_path()
    out_file_flag = str(
        out_file_flag if out_file_flag.startswith("_") else "_" + out_file_flag
    )
    summary_dataset_name = dataset_name + out_file_flag + ".xlsx"
    full_summary_file_path = os.path.join(sumstorpath, summary_dataset_name)
    return full_summary_file_path


def setup_append_spreadsheet(
    raw_gtrends_data_file: str, force_refresh: bool = False
) -> str:
    """First-time setup of data collection and summarizing structure for GTrends data analysis."""
    target_append_dataset = define_target_append_dataset(raw_gtrends_data_file)
    # Check to see if the file already exists
    exists = False
    if os.path.exists(target_append_dataset) is True:
        # The document already exists. Be very careful to not destroy your data!
        print(
            "The",
            os.path.basename(target_append_dataset),
            "summary file already exists.",
        )
        if core.string_to_bool(force_refresh) is True:
            # If you're sure........
            print(
                "  Refreshing the file and building from scratch in",
                os.path.dirname(target_append_dataset),
            )
            os.remove(target_append_dataset)
            exists = False
        else:
            print("\tThe summary file will not be removed or refreshed.")
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
        rc.df_to_file(
            prepped_raw_data,
            target_append_dataset,
            index=False,
            sheet_xlsx=raw_data_collection_file_flag,
        )

    return target_append_dataset


def raw_data_appending_prep(raw_gtrends_data_file: str) -> pd.DataFrame:
    """Functions common to both first init setup of raw data cumulative collection and appending new raw data.
    Returns a transposed version of the input raw data in pd.DataFrame format."""
    raw_data_in_df = rc.file_to_df(raw_gtrends_data_file)
    # Ensure top and rising Qs "value" columns get renamed to 'gtis' for consistency and downstream functionality.
    # # Will not affect DFs without a "value" column.
    raw_data_in_df = raw_data_in_df.rename(columns={"value": "gtis"})
    # Get only the UOA & GTIS
    uoa_col = raw_data_in_df.columns[0]
    subset_raw_data = raw_data_in_df[[uoa_col] + ["gtis"]]
    # Rename the GTIS column with the date of the data pull.
    # That way, you'll be able to tell which raw dataset the GTIS is coming from.
    date_of_data_pull = os.path.splitext(raw_gtrends_data_file)[0][
        (os.path.splitext(raw_gtrends_data_file)[0]).rfind("_") + 1 :
    ]
    formatted_date_of_pull = dt.datetime.strftime(
        dt.datetime.strptime(date_of_data_pull, "%Y%m%d"), "%m/%d/%Y"
    )
    subset_raw_data = subset_raw_data.rename(columns={"gtis": formatted_date_of_pull})
    # Pull the date-of-pull into its own column for easy downstream access?
    # Problem is that lots of UOA access is done by
    # Transpose the subset data for format adhearance downstream.
    transposed_sub_df = rc.transpose_df(
        subset_raw_data,
        first_col_as_new_col_names=True,
        old_cols_as_index=False,
        col_of_oldcolumns_name=date_of_pull_field,
    )
    return transposed_sub_df


def append_raw_data_from_files(
    raw_gtrends_data_files: list, suppress_prints: bool = False
) -> dict:  # pd.DataFrame:
    """Append raw Google Trends data stored as individual files to a larger summary collection of all data collected
    for the same given study time period and geography.
    This function will append all the raw target files (passed as an argument via a list item) to a collection XLSX.
    It will return a dictionary in format {collection XLSX: [list of individual raw target files]}
    Corresponds to Issue #8 in GitHub."""
    if core.string_to_bool(suppress_prints) is not True:
        print("Appending raw files.")
        print()
        stor_folder_labl = "Raw Data Storage File"
        print(
            "{0:25}{1:60}{2}".format(
                "Process Counter", "Single Raw Data File", stor_folder_labl
            )
        )
        print(
            "{0:25}{1:60}{2}".format(
                "-" * 20, "-" * 45, "-" * int(len(stor_folder_labl) * 1.5)
            )
        )
    appcounter = 0

    # Check if the user only passed one file as a string.
    raw_gtrends_data_files = (
        [raw_gtrends_data_files]
        if type(raw_gtrends_data_files) == str
        else raw_gtrends_data_files
    )
    # Get the file count of the raw datasets passed
    allfilscnt = len(raw_gtrends_data_files)

    # Find the summary dataset which to append the data.
    all_datasets_dict = (
        {}
    )  # A dictionary with append_dataset: [list_of_raw_files_to_append]
    for rf in raw_gtrends_data_files:  # For raw file in all the raw data files
        target_append_dataset = define_target_append_dataset(rf)
        # Add the connection between raw and append datasets to a dictionary.
        if target_append_dataset not in all_datasets_dict:
            # If not, create a new list with the current rf
            all_datasets_dict[target_append_dataset] = [rf]
        else:
            # If it exists, append rf to the existing list
            all_datasets_dict[target_append_dataset].append(rf)

    # Check if the target append datasets all exist.
    for app_spreadsheet in all_datasets_dict:
        first_raw_entry = all_datasets_dict[app_spreadsheet][0]
        # for each raw data records XLSX:
        if os.path.exists(app_spreadsheet) is False:
            # # Do stuff to setup the summary xlsx with the current raw data as its first entry.
            # setup_file = setup_append_spreadsheet(first_raw_entry)
            # # Load the entire XLSX that only has the one column.
            appended_df = (
                None  # rc.file_to_df(setup_file)  # ,raw_data_collection_sheet)
            )
            init_setup = True
        else:
            # Pull in the existing raw data records
            appended_df = rc.file_to_df(app_spreadsheet)
            init_setup = False
        # try:
        # Loop through the raw datasets that need to be added to this collection of raw data dataset.
        non_nulls = 0
        for raw_gtrends_data_file in all_datasets_dict[app_spreadsheet]:
            # Prepare your new raw data
            prepped_raw_data = raw_data_appending_prep(raw_gtrends_data_file)
            if not suppress_prints:
                non_nulls += len(prepped_raw_data.dropna(how="all"))
            # Only execute if the item is not the first in its list for an initial setup.
            if (
                not init_setup or raw_gtrends_data_file != first_raw_entry
            ) and appended_df is not None:
                # Append the data to the stuff that is already there.
                # # If using indexes: https://stackoverflow.com/a/34236431/15517267
                # df.loc[["x", "y"]]
                # # https://stackoverflow.com/questions/71545135/how-to-append-rows-with-concat-to-a-pandas-dataframe
                appended_df = pd.concat([appended_df, prepped_raw_data])
            else:
                # You essentially have the format you need already set up if this is the first record in the append dataset.
                appended_df = prepped_raw_data
            appcounter += 1
            if not core.string_to_bool(suppress_prints):
                # Format appcounter with leading spaces
                total_width = len(str(allfilscnt))
                formatted_counter = "{:>{width}}".format(appcounter, width=total_width)
                # print(f"{formatted_counter} / {allfilscnt} processed:\t{os.path.basename(raw_gtrends_data_file)}\tadded to {os.path.basename(app_spreadsheet)}")
                print(
                    "{0:25}{1:60}{2}".format(
                        f"{formatted_counter} / {allfilscnt} processed:",
                        os.path.basename(raw_gtrends_data_file),
                        os.path.basename(app_spreadsheet),
                    )
                )
        # del init_setup

        # Edit and format the resulting all-raw-data dataframe
        # # Pull this out of the `for each raw data file` loop b/c this only needs to be done once per append dataset.
        # # # So do it at the end.
        # 0s seem to mean something wonky with the data source has gone on. We don't want those. Null out the 0s.
        appended_df = appended_df.replace(0, np.nan)
        # Sort by date to get the earliest rows on top.
        # # This is sorting 2023 early months over 2022 late months. Need the opposite.
        # # Convert field to datetime
        appended_df[date_of_pull_field] = pd.to_datetime(
            appended_df[date_of_pull_field], format="%m/%d/%Y"
        )
        # # Sort with the most recently added data on top.
        appended_df = appended_df.sort_values(by=date_of_pull_field, ascending=False)
        # # Re-convert the date field to a favorable text format for output printing.
        appended_df[date_of_pull_field] = appended_df[date_of_pull_field].dt.strftime(
            "%m/%d/%Y"
        )
        # Drop any rows that are complete duplicates.
        # # This should keep rows with the same data collection date as long as the values are different.
        # # This way we could presumably take multiple data measurements on the same day,
        # # # collect different data, and use them all.
        # https://stackoverflow.com/questions/23667369/drop-all-duplicate-rows-across-multiple-columns-in-python-pandas
        appended_df = appended_df.drop_duplicates()

        # except ValueError or NameError:
        #     # While the summary file exists, the raw data tabulation sheet does not.
        #     # Create it and set this prepped raw data as the first record in the tab.
        #     # setup_file = setup_summary_spreadsheet(raw_gtrends_data_file)
        #     appended_df = prepped_raw_data  # rc.file_to_df(setup_file, raw_data_collection_sheet)

        # Output this data back to its original path.
        # # Do this by hard resetting/overwriting that file; there is no reason we need to update it.
        rc.df_to_file(
            appended_df,
            app_spreadsheet,
            add_to_existing_xlsx=False,
            sheet_xlsx=raw_data_collection_file_flag,
            overwrite_old_sheet=True,
        )
        # if not core.string_to_bool(suppress_prints):
        #     # non_nulls = len(appended_df.dropna(how='all'))
        #     print(f"Added {str(non_nulls)} datasets from {len(all_datasets_dict[app_spreadsheet])} {'raw_gtrends_data_files'.replace('_',' ')} to {os.path.basename(app_spreadsheet)}.")

    if core.string_to_bool(suppress_prints) is not True:
        print("\n-----------------------------------------------\n")

    return all_datasets_dict


def append_all_raw_files(raw_files_parent_dir: str, suppress_prints=False):
    """Append the data from all of the raw data files in the directory passed as an argument.
    Corresponds to Issue #8 in GitHub."""
    if os.path.exists(raw_files_parent_dir):
        all_raw_files = [
            os.path.join(raw_files_parent_dir, rf)
            for rf in os.listdir(raw_files_parent_dir)
            if (rf.endswith(".csv") or rf.endswith(".xlsx"))
        ]
        appfiles_and_their_rawdata = append_raw_data_from_files(
            all_raw_files, suppress_prints=suppress_prints
        )
        return appfiles_and_their_rawdata
    else:
        print("Does not exist as a file directory:", raw_files_parent_dir)
        print("  Try", store.get_storage_path())
        return store.get_storage_path()


if __name__ == "__main__":
    import time

    start = time.time()

    def individual_appends():
        tstfil = os.path.expanduser(
            r"~\NACCRRA\Research Team - Documents\Mapping\google_trends\gtrends_data\raw_data\eugene_time_20200214-20210214_20231214.csv"
        )
        anothertestfil = os.path.expanduser(
            r"~\NACCRRA\Research Team - Documents\Mapping\google_trends\gtrends_data\raw_data\eugene_time_20200214-20210214_20231208.csv"
        )
        vtines_list = [
            os.path.expanduser(
                r"~\NACCRRA\Research Team - Documents\Mapping\google_trends\gtrends_data\raw_data\valentines_dma_df_20200214-20210214_20231212.csv"
            ),
            os.path.expanduser(
                r"~\NACCRRA\Research Team - Documents\Mapping\google_trends\gtrends_data\raw_data\valentines_dma_df_20200214-20210214_20231209.csv"
            ),
        ]
        additional_vtines = [
            os.path.expanduser(
                r"~\NACCRRA\Research Team - Documents\Mapping\google_trends\gtrends_data\raw_data\valentines_dma_df_20200214-20210214_20231207.csv"
            ),
            os.path.expanduser(
                r"~\NACCRRA\Research Team - Documents\Mapping\google_trends\gtrends_data\raw_data\valentines_dma_df_20200214-20210214_20231214.csv"
            ),
        ]
        two_uoas = [
            os.path.expanduser(
                r"~\NACCRRA\Research Team - Documents\Mapping\google_trends\gtrends_data\raw_data\mn_time_20200214-20210214_20231208.csv"
            ),
            os.path.expanduser(
                r"~\NACCRRA\Research Team - Documents\Mapping\google_trends\gtrends_data\raw_data\mn_time_20200214-20210214_20231206.csv"
            ),
            os.path.expanduser(
                r"~\NACCRRA\Research Team - Documents\Mapping\google_trends\gtrends_data\raw_data\valentines_dma_df_20200214-20210214_20231204.csv"
            ),
        ]
        print(define_target_append_dataset(two_uoas[0]))
        ret_df = append_raw_data_from_files(two_uoas)
        return ret_df

    def full_run_test(rawfildir: str = None):
        """Test the full run appending every file in the directory"""
        if not rawfildir:
            rawfildir = os.path.expanduser(
                r"~\NACCRRA\Research Team - Documents\Mapping\google_trends\gtrends_data\raw_data"
            )
        return append_all_raw_files(
            raw_files_parent_dir=rawfildir, suppress_prints=False
        )

    # full_run_test()

    core.runtime(start)
