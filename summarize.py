"""
This file will calculate summary statistics for raw google trends data that you pull.
The results of this file should give you meaningful, reportable results.
Goal: use the append data columns to calc in a new XLSX with each column's (eg, state, DMA, or date
(day, week, month, etc whatever the temporal UOA was)) summary stats. Will have the same column headers as append dataset.
The only difference will be the rows: raw data values collected into one sheet or summary stats of that data.
Similar (but not identical) to the SSM GD6/7s or map notes.
"""

import os, time, numpy as np, pandas as pd
from pathlib import Path

from ccaoa import core, raccoon as rc


try:
    from . import dma, store_data as store, trend_calculations as tcalc, append as app
except ImportError:
    import dma, store_data as store, trend_calculations as tcalc, append as app


# Need to Transpose the individual data pull records, append them to the master pull list, and recalc the sum stats.
# May be somewhat similar to Graph Data 6, but output multiple tabs in 1 XLSX:
# * GD6-esque record-level list (from which the sum stats will be calculated)
# * Sum Stats (top 3 lines from the old GTrends xlsxs) with every var re-transposed to be the record and their
#   * Average
#   * Std Dev
#   * N
#   * Coverage Factor
#   * Expanded Uncertainty
summary_stats_file_flag = "summary_stats"
date_of_pull_field = app.date_of_pull_field
gtis_average_field = app.gtis_average_field


def define_target_summary_dataset(
    raw_or_append_data_file: str, out_file_flag: str = summary_stats_file_flag
) -> str:
    """Use the name of the raw data file to target which summary Xlsx you'll be using."""
    if os.path.exists(raw_or_append_data_file) is False:
        raise FileNotFoundError(raw_or_append_data_file)
    # Get the input file's basename
    dataset_name = Path(raw_or_append_data_file).stem
    # Remove the append file naming convention
    dataset_name = dataset_name.replace(app.raw_data_collection_file_flag, "")
    # Replace the file naming flag with the summary stats flag.
    dataset_name = dataset_name[: dataset_name.rfind("_")]
    sumstorpath = app.summary_storage_path()
    out_file_flag = str(
        out_file_flag if out_file_flag.startswith("_") else "_" + out_file_flag
    )
    summary_dataset_name = dataset_name + out_file_flag + ".xlsx"
    full_summary_file_path = os.path.join(sumstorpath, summary_dataset_name)
    return full_summary_file_path


def calc_sumstats(appended_data_xlsx: str, coverage_factor_k=2, gtis_sort=True):
    """
    Calculate the Summary Statistics (top 3 lines from the old GTrends xlsxs):
        * Average
        * Std Dev
        * N
        * Standard Error
        * Confidence Interval
        * Coverage Factor
        * Expanded Uncertainty
        * Rebased GTIS
    """
    # Get data as it is

    # # What if we pulled this out of this function to make it a purely mathmatical one?
    # try:
    #     sumstats_df = rc.file_to_df(summary_xlsx,summary_stats_sheet)
    # except ValueError or NameError:
    #     # The summary doc that exists does not have the summary_stats_sheet for some reason.
    #     # Use an empty working dataframe going forward.
    #     sumstats_df = pd.DataFrame()
    #     # # After testing for Issue #6, it was determined that the rc.df_to_file() at the end of this function is
    #     # # # sufficient to add the summary_stats_sheet as a new sheet to the XLSX, even with `add_to_existing_xlsx=True`
    #     # # # and `overwrite_old_sheet=True` arguments.
    #     # # So, we don't need to artificially create the sheet here; it'll get handled later.
    #     # rc.df_to_file(sumstats_df, summary_xlsx, sheet_xlsx=summary_stats_sheet, add_to_existing_xlsx=True)
    #
    sumstats_df = pd.DataFrame()

    raw_data_df = rc.file_to_df(appended_data_xlsx)  # , raw_data_collection_sheet)
    # SumStats Vars not previously defined
    # gtis_average_field  # Previously defined
    # UOA Column. Needs to be dynamic to work with time or geography UOA.
    uoa_col = (os.path.basename(appended_data_xlsx)).split("_")[1]  # 'dma'
    covfactfield = "cov_fact_k"
    std_dev_col = "std_dev"
    xpduncertainfield = "expd_uncrt"
    rebase_gtis_field = "rebse_gtis"
    n_field = "n_data_pts"
    se_field = "std_err"
    moe_field = "moe_95_pct"
    ci_95_fld = "ci_95_pct"
    ci_95_lowr_fld = "ci_95_lowr"
    ci_95_uppr_fld = "ci_95_uppr"
    # Order the output fields.
    sumstatvars = [
        uoa_col,
        gtis_average_field,
        n_field,
        std_dev_col,
        se_field,
        moe_field,
        ci_95_lowr_fld,
        ci_95_uppr_fld,
        rebase_gtis_field,
        covfactfield,
        xpduncertainfield,
        ci_95_fld,
    ]

    # CALCULATIONS
    # Ensure the UOA records are all in the sum stats sheet.
    transposed_sub_df = rc.transpose_df(
        raw_data_df,
        first_col_as_new_col_names=True,
        old_cols_as_index=False,
        col_of_oldcolumns_name=date_of_pull_field,
    )
    sumstats_df[uoa_col] = transposed_sub_df[date_of_pull_field]  # 'pull_date'
    # Add dma_id column if it's a Media Market (DMA) UOA.
    # # This code cannot appear any earlier than here because this is where the UOA's column values are defined,
    # # # and that is a prerequisite to assign the correct DMA ID (if it's a DMA UOA).
    if uoa_col.lower() == "dma":
        dma_id_col = "dma_id"
        # Add dma_id_col in as a column in the summary DF and fill the column in with the appropriate dma_id value.
        sumstats_df[dma_id_col] = sumstats_df[uoa_col].apply(
            lambda x: dma.dma_id_name_converter(x)
        )
        # Now insert the dma_id_col as the second column in the final formatting of the columns' order.
        sumstatvars.insert(1, "dma_id")
    # Mean/Average
    sumstats_df[gtis_average_field] = sumstats_df[uoa_col].apply(
        lambda d: raw_data_df[d].mean()
    )
    # Standard Deviation
    sumstats_df[std_dev_col] = sumstats_df[uoa_col].apply(
        lambda d: raw_data_df[d].std()
    )
    # Count n(Observations)
    sumstats_df[n_field] = sumstats_df[uoa_col].apply(lambda d: raw_data_df[d].count())
    # Confidence Interval
    # # Standard Error first.
    sumstats_df[se_field] = sumstats_df[std_dev_col] / np.sqrt(sumstats_df[n_field])
    # # Margin of Error second.
    # # # Using 1.96 as the factor here because I have somewhat normally distributed GTrends data,
    # # # # and the sample size (and thus the degrees of freedom) is very large.
    # # # Later, you may want to make this a function and if sample size < 30,
    # # # # assume t distribution and calc a different factor.
    # # # # e.g., `confidence_factor = scipy.stats.t.ppf((1 + confidence_level) / 2, df=degrees_of_freedom)`
    factor_moe = 1.96
    sumstats_df[moe_field] = sumstats_df[se_field] * factor_moe
    # # Now, calculate the confidence interval
    sumstats_df[ci_95_fld] = [
        (average - moe, average + moe)
        for average, moe in zip(sumstats_df[gtis_average_field], sumstats_df[moe_field])
    ]
    sumstats_df[ci_95_lowr_fld] = (
        sumstats_df[gtis_average_field] - sumstats_df[moe_field]
    )
    sumstats_df[ci_95_uppr_fld] = (
        sumstats_df[gtis_average_field] + sumstats_df[moe_field]
    )
    # Coverage Factor
    sumstats_df[covfactfield] = coverage_factor_k
    # Expanded Uncertainty
    sumstats_df[xpduncertainfield] = sumstats_df[uoa_col].apply(
        lambda d: tcalc.uncertainty_df_field(raw_data_df, d)
    )
    # Rebase the maximum mean GTIS to = 100 to get a more "google trendy" result.
    sumstats_df[rebase_gtis_field] = sumstats_df[gtis_average_field].apply(
        lambda m: tcalc.rebase_math(m, sumstats_df[gtis_average_field].max())
    )
    # Sort to have the most popular on top if the argument passed requests it.
    # # Generally, we'll want to have geography fields (states & DMAs, etc) sorted by GTIS and time sorted by time.
    if gtis_sort:
        if "time" in uoa_col.lower():
            # Sort by the event time if it's a temporal dataset.
            sumstats_df = sumstats_df.sort_values(by=uoa_col, ascending=True)
        else:
            # Sort by GTIS if it's a geographic dataset.
            sumstats_df = sumstats_df.sort_values(
                by=[gtis_average_field, uoa_col], ascending=[False, True]
            )

    # Now retain only the columns we want + order them in the desired order defined above in the `sumstatvars` variable.
    sumstats_df = sumstats_df[sumstatvars]

    # Rename key columns now that they're filtered down to the ones we want.
    # # Format: # new_column_names = {'old_column_name1': 'new_column_name1','old_column_name2': 'new_column_name2'}
    the_renamed_fields = {}
    temporal_uoa_sumstats_colname = "event_time"
    all_renames = {
        # UOA field renames
        # # No DMA change
        # # States
        "states": "state",
        # # Query terms
        "rising": "rising_term",
        "query": "term",
        "top": "top_term",
        # # 'temporal'
        # # # Avoids confusion with pull_date vs event time as the UOA Google's measuring.
        "time": temporal_uoa_sumstats_colname,
        "temporal": temporal_uoa_sumstats_colname,
        "date": temporal_uoa_sumstats_colname,
        # No other non-UOA columns need to be renamed until further notice.
    }
    uoalower = uoa_col.lower()
    if uoalower in all_renames:
        # The UOA needs to be renamed
        the_renamed_fields[uoa_col] = all_renames[uoalower]
    # Execute the rename
    if bool(the_renamed_fields):
        # i.e., if the dictionary containing the names of the columns that need to be renamed is not empty,
        # # then there are columns needing to be renamed
        sumstats_df.rename(columns=the_renamed_fields, inplace=True)
    # If you need to access a fresh all-columns list with the renamed columns:
    # sumstats_df.columns.to_list()
    # print(sumstats_df.columns)

    # Write the results to the appropriate summary XLSX, separate from the appended raw data since >v0.0.4.
    summary_xlsx = define_target_summary_dataset(appended_data_xlsx)
    rc.df_to_file(
        sumstats_df,
        summary_xlsx,
        sheet_xlsx=summary_stats_file_flag,
        add_to_existing_xlsx=False,
    )

    return sumstats_df


# The following functions employ the above to process multiple files simultaneously.


def summarize_collected_data(
    list_of_appended_datasets: list, suppress_prints: bool = False
):
    """
    Use a list of appended xlsx datasets representing distinct and unique G Trends instances for which you're collecting
    samples and summarize all the raw data records already recorded in the summary sheets.
    """
    if core.string_to_bool(suppress_prints) is not True:
        print("Summarizing files.")
        print()
        source_data_labl = "Raw Data Storage File"
        stor_fil_labl = "Summary Statistics File"
        print(
            "{0:25}{1:65}{2}".format("Process Counter", source_data_labl, stor_fil_labl)
        )
        print(
            "{0:25}{1:65}{2}".format(
                "-" * 20, "-" * 45, "-" * int(len(stor_fil_labl) * 1.5)
            )
        )
    sumcounter = 0
    allfilscnt = len(list_of_appended_datasets)
    for sd in list_of_appended_datasets:
        # print(os.path.basename(sd))
        calc_sumstats(sd)
        sumcounter += 1
        if core.string_to_bool(suppress_prints) is not True:
            # Format sumcounter with leading spaces
            total_width = len(str(allfilscnt))
            formatted_counter = "{:>{width}}".format(sumcounter, width=total_width)
            sumstats_spreadsheet = define_target_summary_dataset(sd)
            print(
                "{0:25}{1:65}{2}".format(
                    f"{formatted_counter} / {allfilscnt} processed:",
                    os.path.basename(sd),
                    os.path.basename(sumstats_spreadsheet),
                )
            )
            # print(f"{formatted_counter} / {allfilscnt} processed:\t{os.path.basename(sd)}\tadded to {os.path.basename(sumstats_spreadsheet)}")
            # print(counter, '/', allfilscnt, "processed:   ", os.path.basename(sd))
    if core.string_to_bool(suppress_prints) is not True:
        print("\n-----------------------------------------------\n")


def summarize_all_appended_data(
    summary_files_parent_dir: str, suppress_prints: bool = False
):
    """Summarize all the appended data already added to the summary sheet from all of the raw data files.
    Takes the directory housing the summary files as an argument.
     Corresponds to Issue #9  in GitHub:"""
    if os.path.exists(summary_files_parent_dir):
        # Filter down to only the append files that hold all the raw data records.
        all_agg_files = [
            os.path.join(summary_files_parent_dir, af)
            for af in os.listdir(summary_files_parent_dir)
            if af.endswith(app.raw_data_collection_file_flag + ".xlsx")
        ]
        summarize_collected_data(all_agg_files, suppress_prints=suppress_prints)
        return all_agg_files
    else:
        print("Does not exist as a file directory:", summary_files_parent_dir)
        return None


def full_append_and_summary_run(
    raw_files_dir=store.get_storage_path(),
    summary_files_dir=app.summary_storage_path(),
    suppress_prints=False,
):
    """Using ALL of the files stored in the `raw_files_dir`, append them ALL to their summary.xlsx.
    Then, summarize the statistics of all of these raw datasets.
    This represents a clean workflow that builds all. summary XLSXs from the ground up.
    """

    # Check the arguments for validity.
    if not os.path.exists(raw_files_dir):
        raise FileNotFoundError(raw_files_dir)
    if not os.path.exists(summary_files_dir):
        raise FileNotFoundError(summary_files_dir)
    try:
        suppress_prints = core.string_to_bool(suppress_prints)
    except:
        # Restore the default and keep chugging.
        suppress_prints = False

    # Append all raw GTrends data files' contents to their summary XLSX datasets.
    if not suppress_prints:
        print("\nBEGINNING RAW DATA APPENDING...\n")
    app.append_all_raw_files(raw_files_dir, suppress_prints=suppress_prints)
    time.sleep(5)
    # Summarize all those files now.
    if not suppress_prints:
        print("\nSUMMARIZING CONSOLIDATED RAW DATA...\n")
    all_sum_fils = summarize_all_appended_data(
        summary_files_dir, suppress_prints=suppress_prints
    )

    return all_sum_fils


if __name__ == "__main__":
    start = time.time()

    raw_data_pth = store.get_storage_path()  # os.path.join(base_path,"raw_data")
    sum_data_pth = app.summary_storage_path()  # os.path.join(base_path, "summary_data")

    # # Summarize the already-appended data
    # summarize_all_appended_data(sum_data_pth)

    # Full run to completely recreate all the summary files!
    full_append_and_summary_run()

    core.runtime(start)
