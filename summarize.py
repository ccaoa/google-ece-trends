"""
This file will calculate summary statistics for raw google trends data that you pull.
The results of this file should give you meaningful, reportable results.
"""

import os, datetime as dt, numpy as np, pandas as pd
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
#     """Append raw Google Trends data stored as an individual file to a larger summary collection of all data collected
#     for the same given study time period and geography."""
raw_data_collection_sheet = "raw_data_records"
summary_stats_sheet="summary_stats"
date_of_pull_field = "pull_date"
gtis_average_field = "gtis_mean"


def raw_data_appending_prep(raw_gtrends_data_file):
    """ Functions common to both first init setup of raw data cumulative collection and appending new raw data."""
    raw_data_in_df = core.file_to_df(raw_gtrends_data_file)
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


def setup_summary_spreadsheet(raw_gtrends_data_file,force=False):
    """ First-time setup of data collection and summarizing structure for GTrends data analysis. """
    basename = os.path.basename(raw_gtrends_data_file)
    target_summary_dataset = define_target_summary_dataset(raw_gtrends_data_file)
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
            return

    # If the script makes it here, the summary spreadsheet does not yet exit. So create it!
    # # The conditional here may not be necessary
    if exists is False:
        # Create the summary spreadsheet from the raw data.

        # FIRST: We need to setup the raw data records collection sheet. All future raw data will be appended here.
        # All we need are the UOA column (eg, date, dma, state, etc) and the GTIS.
        # # The UOA col will be the first one b/c of data formatting in `pull_data.py`.
        prepped_raw_data = raw_data_appending_prep(raw_gtrends_data_file)
        # Output the first sheet/tab of the xlsx to = the transposed data & the GTIS.
        core.df_to_file(prepped_raw_data,target_summary_dataset,index=False,sheet_xlsx=raw_data_collection_sheet)

        # SECOND: Setup a second tab/sheet in the xlsx that does mathematical calculations for the raw dataset.
        # # After the transpose, the UOA features are now the new columns.
        # # They will also become the columns for the summary stats data.
        # stats_df = transposed_sub_df.copy()
        # # One way to do it is keep the dates as the columns and add rows:
        # pd.concat([mnsubsettransposetime, pd.DataFrame(index=["IDXbaby"]), pd.DataFrame(index=['haha'])], axis=0,
        #           ignore_index=False)
        # Or, it could revert to dates being rows and the GTIS and error etc are column headers since that's the primary study var for this dataset.
        stats_df = core.file_to_df(raw_gtrends_data_file)
        # We only need the UOA and the GTIS (and maybe keep the DMA ID/state FIPS), nothing else
        dropcols = ['rank','isPartial']
        stats_df = stats_df.drop(columns=[c for c in stats_df.columns if c in dropcols])
        # Rename the GTIS field to make it clear that it's the average GTIS, not a single record.
        stats_df = stats_df.rename(columns={'gtis':gtis_average_field})
        # The rest of the calcs will be shared by downstream processes, so write function for that.
        # All we need to do now is to setup the basic infrastructure, ie a second tab with a stable tab name.
        core.df_to_file(stats_df,target_summary_dataset,index=False,sheet_xlsx=summary_stats_sheet, add_to_existing_xlsx=True)

        return target_summary_dataset
    else:
        return None


def append_raw_data_fromfile(raw_gtrends_data_file):
    """ Append raw Google Trends data stored as an individual file to a larger summary collection of all data collected
    for the same given study time period and geography."""
    # Find the summary dataset which to append the data.
    target_summary_dataset = define_target_summary_dataset(raw_gtrends_data_file)
    if os.path.exists(target_summary_dataset) is False:
        # Do stuff to setup the summary xlsx with the current raw data as its first entry.
        setup_file = setup_summary_spreadsheet(raw_gtrends_data_file)
        appended_df = core.file_to_df(setup_file,raw_data_collection_sheet)
    else:
        # Append the data to the stuff that is already there.
        # Prepare your new raw data
        prepped_raw_data = raw_data_appending_prep(raw_gtrends_data_file)
        # Pull in the existing raw data records
        existing_raw_records = core.file_to_df(target_summary_dataset, raw_data_collection_sheet)
        # # If using indexes: https://stackoverflow.com/a/34236431/15517267
        # df.loc[["x", "y"]]
        # # https://stackoverflow.com/questions/71545135/how-to-append-rows-with-concat-to-a-pandas-dataframe
        appended_df = pd.concat([existing_raw_records,prepped_raw_data])
        # Sort by date to get the earliest rows on top.
        appended_df = appended_df.sort_values(by=date_of_pull_field, ascending=True)
        # 0s seem to mean something wonky with the data source has gone on. We don't want those. Null out the 0s.
        appended_df = appended_df.replace(0,np.nan)
        # Drop any rows that are complete duplicates.
        # # This should keep rows with the same data collection date as long as the values are different.
        # # This way we could presumably take multiple data measurements on the same day,
        # # # collect different data, and use them all.
        # https://stackoverflow.com/questions/23667369/drop-all-duplicate-rows-across-multiple-columns-in-python-pandas
        appended_df = appended_df.drop_duplicates()
        # Output this data back into its original tab.
        core.df_to_file(appended_df,target_summary_dataset,add_to_existing_xlsx=True,sheet_xlsx=raw_data_collection_sheet,overwrite_old_sheet=True)

    return appended_df


def calc_sumstats(summary_xlsx, coverage_factor_k=2):
    """ 
    Calculate the Summary Statistics (top 3 lines from the old GTrends xlsxs):
        * Average
        * Std Dev
        * N
        * Coverage Factor
        * Expanded Uncertainty
        * Rebased GTIS
    """
    # Get data as it is
    sumstats_df = core.file_to_df(summary_xlsx,summary_stats_sheet)
    raw_data_df = core.file_to_df(summary_xlsx, raw_data_collection_sheet)
    # SumStats Vars not previously defined
    # gtis_average_field  # Previously defined
    dma_col = 'dma'
    covfactfield='cov_fact_k'
    std_dev_col = 'std_dev'
    xpduncertainfield='expd_uncrt'
    rebase_gtis_field = 'rebse_gtis'
    n_field = 'n_data_pts'

    # CALCULATIONS
    # Mean/Average
    # sumstats_df[gtis_average_field] = raw_data_df[sumstats_df[dma_col]].mean()  # Did not work in current form
    # sumstats_df[gtis_average_field] = raw_data_df[sumstats_df[dma_col]].mean()
    # sumstats_df[gtis_average_field] = raw_data_df[sumstats_df[dma_col]][sumstats_df[dma_col]].mean()
    # sumstats_df[gtis_average_field] = [raw_data_df[d] for d in sumstats_df[dma_col]]#[sumstats_df[dma_col]]].mean()
    # [raw_data_df[d].mean() for d in sumstats_df[dma_col]]
    sumstats_df[gtis_average_field] = sumstats_df[dma_col].apply(lambda d: raw_data_df[d].mean())
    # Standard Deviation
    sumstats_df[std_dev_col] = sumstats_df[dma_col].apply(lambda d: raw_data_df[d].std())
    # Coverage Factor
    sumstats_df[covfactfield]=coverage_factor_k
    # Expanded Uncertainty
    # # TROUBLESHOOT UNCERTAINTY; IT IS PRODUCING ONLY STD_DEV IN OUTPUT.
    sumstats_df[xpduncertainfield]=sumstats_df[dma_col].apply(lambda d: tcalc.uncertainty_df_field(raw_data_df,d))
    # Count n(Observations)
    sumstats_df[n_field]=sumstats_df[dma_col].apply(lambda d: raw_data_df[d].count())
    # Rebase the maximum mean GTIS to = 100 to get a more "google trendy" result.
    sumstats_df[rebase_gtis_field]=sumstats_df[gtis_average_field].apply(lambda m: tcalc.rebase_math(m,sumstats_df[gtis_average_field].max()))
    # The above is a working version of rebase. Test with a dataset that does not have a mean GTIS = 100 (eg TX dataset)

    # Write the results back to the XLSX
    core.df_to_file(sumstats_df,summary_xlsx, sheet_xlsx=summary_stats_sheet)

    return sumstats_df


if __name__ == '__main__':
    import time
    start = time.time()

    # RAW DATA TESTING FILES
    # # Base path for multi-machine testing.
    # base_path = os.path.expanduser(r"~\NACCRRA\Research Team - Documents\Mapping\google_trends\gtrends_data")
    base_path = os.path.expanduser(r"~\Documents\Coding\Git\GitHub\ccaoa_github\gtrends_data")
    # Minnesota
    tsttimepath= os.path.join(base_path, r"raw_data\mn_time_20200214-20210214_20221212.csv")
    tstgeogpath= os.path.join(base_path, r"raw_data\mn_dma_20200214-20210214_20221212.csv")
    geogappndpth= os.path.join(base_path, r"raw_data\mn_dma_20200214-20210214_20221209.csv")
    # Oregon
    ordmafil1= os.path.join(base_path, r"raw_data\or_dma_20200214-20210214_20221210.csv")
    ordmafil2 =  os.path.join(base_path, r"raw_data\or_dma_20200214-20210214_20221206.csv")
    # orfil1 later pull than ordmafil2
    # Texas
    # txtdmapth1= os.path.join(base_path, r"raw_data\tx_dma_20210321-20210421_20221207.csv")
    # txtdmapth2= os.path.join(base_path, r"raw_data\tx_dma_20210321-20210421_20221208.csv")
    # txtdmapth3= os.path.join(base_path, r"raw_data\tx_dma_20210321-20210421_20221209.csv")
    # txtdmapth4= os.path.join(base_path, r"raw_data\tx_dma_20210321-20210421_20221212.csv")
    # txtimepth2= os.path.join(base_path, r"raw_data\tx_time_20210321-20210421_20221216.csv")
    txtdmapth1= os.path.join(base_path, r"raw_data\tx_dma_20210321-20210421_20221218.csv")
    txtdmapth2= os.path.join(base_path, r"raw_data\tx_dma_20210321-20210421_20221226.csv")
    txtdmapth3= os.path.join(base_path, r"raw_data\tx_dma_20210321-20210421_20221228.csv")
    txtdmapth4= os.path.join(base_path, r"raw_data\tx_dma_20210321-20210421_20221229.csv")
    tx_rawdata_fils=[txtdmapth1,txtdmapth2,txtdmapth3,txtdmapth4]

    # # setup test
    # setup_summary_spreadsheet(tstgeogpath, force=True)
    # setup_summary_spreadsheet(tsttimepath, force=True)
    # setup_summary_spreadsheet(ordmafil1)

    # # Apppend test
    # append_raw_data_fromfile(geogappndpth)
    # append_raw_data_fromfile(ordmafil1)
    [append_raw_data_fromfile(txf) for txf in tx_rawdata_fils]
    # time.sleep(1)
    # append_raw_data_fromfile(ordmafil2)

    # Summary stats calc test
    # summary_xlsx = define_target_summary_dataset(ordmafil2)
    # calc_sumstats(summary_xlsx)

    txsumxlsx = define_target_summary_dataset(txtdmapth4)
    # dftxsumstats = core.file_to_df(txsumxlsx)
    calc_sumstats(txsumxlsx)
    core.runtime(start)
