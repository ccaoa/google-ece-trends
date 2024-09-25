import os, datetime as dt, re
from ccaoa import core
from time import time, sleep

# from pathlib import Path

try:
    from . import (
        pull_data as pull,
        store_data as store,
        dma,
        append as app,
        summarize as agg,
    )
except ImportError:
    import pull_data as pull, store_data as store, dma, append as app, summarize as agg

storage_path = store.get_storage_path()


def full_gtrends_pull(low_search_volume_results=True):
    """Collect custom data for J. A. Cooper (2024) Google Trends publication."""
    # Make sure you have a valid storage location before going to the trouble of running all these trends.
    if storage_path is None or storage_path == "":
        # Cancel out of the run early; there's nowhere to store the data, so no use in continuing till you have that.
        raise FileNotFoundError("Invalid storage path passed:", storage_path)
    # Validate the low search volume flag as a boolean
    low_search_volume_results = core.string_to_bool(low_search_volume_results)

    # Beware of timeout requests:
    # `pytrends.exceptions.ResponseError: The request failed: Google returned a response with code 429.`
    # https://stackoverflow.com/questions/50571317/pytrends-the-request-failed-google-returned-a-response-with-code-429
    google_connection = pull.connect_to_gtrends(retries=8, backoff_factor=0.7)
    # sleep(11)  # >10 second pause to trick the Google API?

    # Establish a dictionary to contain the dataframes for downstream saving.
    filing_dict = {}

    # USA pulls
    # # Remember, the payload is where you pass your study time-period argument
    init_late2022_studyperiod = "2018-06-03 2022-09-10"
    # Establish dictionary list for downstream filing.
    filing_dict[init_late2022_studyperiod] = []
    geog_usa = "US"
    # Build the payload
    usa_payload = pull.payload_builder(
        timeframe=init_late2022_studyperiod,
        geography_broad=geog_usa,
        connection_item=google_connection,
    )  # Default args  # Future: pass your timeframe argument into this func.
    # sleep(11)  # >10 second pause to trick the Google API?
    #
    # Use the extract_data_try(payload_item, spatial_not_temporal=True, region=None, low_volume=True) func
    # to pull relevant data + formatting out of the payload.
    usa_states_df = pull.extract_data_try(
        usa_payload,
        region="states",
        spatial_not_temporal=True,
        low_volume=low_search_volume_results,
    )
    # # sleep(11)  # >10 second pause to trick the Google API?
    usa_temporal_df = pull.extract_data_try(
        usa_payload, spatial_not_temporal=False, low_volume=low_search_volume_results
    )
    # # sleep(11)  # >10 second pause to trick the Google API?
    usa_dma_df = pull.extract_data_try(
        usa_payload,
        spatial_not_temporal=True,
        region="DMA",
        low_volume=low_search_volume_results,
    )

    #
    # # Get related queries
    # usa_top_qs = pull.top_related_queries(usa_payload)
    # # # sleep(11)  # >10 second pause to trick the Google API?
    # usa_rising_qs = pull.rising_related_queries(usa_payload)

    # Collect data to highlight the Cincinnati Problem (The fact that DMAs are inconsistently reported at state level):
    geog_ky = "US-KY"
    # Build the payloads
    # *NOTE: Looks like you can only have 1 payload active at a time. Do all calcs for KY, THEN move on to IN, etc!*
    # So, KY is up first.
    ky_payload = pull.payload_builder(
        geography_broad=geog_ky,
        timeframe=init_late2022_studyperiod,
        connection_item=google_connection,
    )
    # sleep(11)  # >10 second pause to trick the Google API?
    # Pull relevant data
    ky_dma = pull.extract_data_try(
        payload_item=ky_payload,
        spatial_not_temporal=True,
        region="DMA",
        low_volume=low_search_volume_results,
    )
    # sleep(11)
    ky_time = pull.extract_data_try(
        payload_item=ky_payload,
        spatial_not_temporal=False,
        low_volume=low_search_volume_results,
    )
    # sleep(11)
    #
    # Next is Indiana
    geog_in = "US-IN"
    in_payload = pull.payload_builder(
        geography_broad=geog_in,
        timeframe=init_late2022_studyperiod,
        connection_item=google_connection,
    )
    # sleep(11)  # >10 second pause to trick the Google API?
    in_dma = pull.extract_data_try(
        payload_item=in_payload,
        spatial_not_temporal=True,
        region="DMA",
        low_volume=low_search_volume_results,
    )
    # sleep(11)
    in_time = pull.extract_data_try(
        payload_item=in_payload,
        spatial_not_temporal=False,
        low_volume=low_search_volume_results,
    )
    # sleep(11)
    #
    # Finally, Ohio
    geog_oh = "US-OH"
    oh_payload = pull.payload_builder(
        geography_broad=geog_oh,
        timeframe=init_late2022_studyperiod,
        connection_item=google_connection,
    )
    # sleep(11)
    oh_dma = pull.extract_data_try(
        payload_item=oh_payload,
        spatial_not_temporal=True,
        region="DMA",
        low_volume=low_search_volume_results,
    )
    # sleep(11)
    oh_time = pull.extract_data_try(
        payload_item=oh_payload,
        spatial_not_temporal=False,
        low_volume=low_search_volume_results,
    )
    # sleep(11)

    # Filing dictionary work
    u_fil_list = [
        usa_states_df,
        usa_temporal_df,
        usa_dma_df,
        # usa_top_qs,
        # usa_rising_qs,
        ky_dma,
        ky_time,
        in_dma,
        in_time,
        oh_dma,
        oh_time,
    ]
    # Add each df collected to the filing dictionary
    [filing_dict[init_late2022_studyperiod].append(u) for u in u_fil_list]
    # if u not in filing_dict[init_late2022_studyperiod]]  # <- Causes errors https://stackoverflow.com/questions/18548370/pandas-can-only-compare-identically-labeled-dataframe-objects-error

    # Also collect Texas data to compare with the data I collected for annual report 2021
    # # to further explore the Cincinnati Problem (The fact that DMAs are inconsistently reported at state level):
    tx_time_period = "2021-03-21 2021-04-21"  # "2020-02-14 2021-02-14"
    # # Establish dictionary list for downstream filing.
    filing_dict[tx_time_period] = []
    geog_tx = "US-TX"
    # Build the payloads; you can only have 1 payload active at a time.
    tx_payload = pull.payload_builder(
        geography_broad=geog_tx,
        timeframe=tx_time_period,
        connection_item=google_connection,
    )
    # Pull relevant data
    tx_dma = pull.extract_data_try(
        payload_item=tx_payload,
        spatial_not_temporal=True,
        region="DMA",
        low_volume=low_search_volume_results,
    )
    # Original data pull did not include Time, but why not?
    tx_time = pull.extract_data_try(
        payload_item=tx_payload,
        spatial_not_temporal=False,
        low_volume=low_search_volume_results,
    )
    #
    # Filing dictionary work: Add each df collected to the filing dictionary
    u_fil_list = [tx_dma, tx_time]
    [filing_dict[tx_time_period].append(u) for u in u_fil_list]

    # Also include some data from the classic COVID Valentines' study period.
    # Augment the existing OR & MN data with some national spatial data + get some riding and top keywords.
    valentines_time_period = "2020-02-14 2021-02-14"
    # Establish dictionary list for downstream filing.
    filing_dict[valentines_time_period] = []
    # Build the payload
    valentines_usa_payload = pull.payload_builder(
        valentines_time_period,
        geography_broad=geog_usa,
        connection_item=google_connection,
    )
    # sleep(11)  # >10 second pause to trick the Google API?
    valentines_states_df = pull.extract_data_try(
        valentines_usa_payload,
        region="states",
        spatial_not_temporal=True,
        low_volume=low_search_volume_results,
    )
    # sleep(11)  # >10 second pause to trick the Google API?
    valentines_temporal_df = pull.extract_data_try(
        valentines_usa_payload,
        spatial_not_temporal=False,
        low_volume=low_search_volume_results,
    )
    # sleep(11)  # >10 second pause to trick the Google API?
    valentines_dma_df = pull.extract_data_try(
        valentines_usa_payload,
        spatial_not_temporal=True,
        region="DMA",
        low_volume=low_search_volume_results,
    )
    # sleep(11)  # >10 second pause to trick the Google API?
    #
    # # Get related queries
    # valentines_top_qs = pull.top_related_queries(valentines_usa_payload)
    # # sleep(11)  # >10 second pause to trick the Google API?
    # valentines_rising_qs = pull.rising_related_queries(valentines_usa_payload)
    #
    # Pull state-level OR & MN data to demonstrate how the Cincy Problem has been resolved by Google
    # # since March - April 2021 when original MN & OR data was collected.
    # 1st, MN
    geog_mn = "US-MN"
    mn_payload = pull.payload_builder(
        geography_broad=geog_mn,
        timeframe=valentines_time_period,
        connection_item=google_connection,
    )
    mn_dma = pull.extract_data_try(
        payload_item=mn_payload,
        spatial_not_temporal=True,
        region="DMA",
        low_volume=low_search_volume_results,
    )
    mn_time = pull.extract_data_try(
        payload_item=mn_payload,
        spatial_not_temporal=False,
        low_volume=low_search_volume_results,
    )
    # Then, Oregon
    geog_or = "US-OR"
    or_payload = pull.payload_builder(
        geography_broad=geog_or,
        timeframe=valentines_time_period,
        connection_item=google_connection,
    )
    or_dma = pull.extract_data_try(
        payload_item=or_payload,
        spatial_not_temporal=True,
        region="DMA",
        low_volume=low_search_volume_results,
    )
    or_time = pull.extract_data_try(
        payload_item=or_payload,
        spatial_not_temporal=False,
        low_volume=low_search_volume_results,
    )
    # Also include Eugene, Oregon to look within a DMA for kicks and longitudinal consistency.
    # # The Beaver/Duck DMA!
    # To construct the geography, we need that DMA ID. Dynamically access it.
    beaver_duck_dma_name = next(
        key for key in dma.dma_name_to_id_dict() if "Eugene" in key
    )
    beaver_duck_dma_id = str(dma.dma_id_name_converter(beaver_duck_dma_name))
    geog_eugene = geog_or + "-" + beaver_duck_dma_id
    # Then, go on collecting data like normal.
    eugene_payload = pull.payload_builder(
        geography_broad=geog_eugene,
        timeframe=valentines_time_period,
        connection_item=google_connection,
    )
    eugene_time = pull.extract_data_try(
        payload_item=eugene_payload,
        spatial_not_temporal=False,
        low_volume=low_search_volume_results,
    )
    # # A City-level UOA pull!
    # # Turns out this is harder than I thought. Some issues with Cities. See pull_data.py for more on this.
    # # For now, if you try to use 'city' as your region, you'll either get:
    # # # A) an error (DMA as payload geog), or
    # # # B) DMA results (State as payload geog).
    # # This is a known limitation of the pytrends package as of <v4.9.2
    # eugene_city = pull.extract_data_try(payload_item=eugene_payload, spatial_not_temporal=True, region='city', low_volume=low_search_volume_results)
    #
    # Filing dictionary work
    v_fil_list = [
        valentines_states_df,
        valentines_temporal_df,
        valentines_dma_df,
        # valentines_top_qs,
        # valentines_rising_qs,
        mn_dma,
        mn_time,
        or_dma,
        or_time,
        eugene_time,
    ]  # , eugene_city]
    # Add each df collected to the filing dictionary
    [filing_dict[valentines_time_period].append(v) for v in v_fil_list]

    # NEXT: Store all the data for all of the dataframes generated here.
    # Storage paths now dynamically set above.
    # print(f"Data will be stored in '{storage_path}'.")
    # Set the stage for reprocessing previously failed data collection efforts.
    dfs_to_process = 0
    # Count all the DFs to process
    for timeframe in filing_dict:
        dfs_to_process += len(filing_dict[timeframe])
    today = dt.datetime.today().strftime("%Y-%m-%d")
    print(
        f"Will attempt to store {dfs_to_process} datasets on {today} in '{storage_path}'.\n-----------------------------------------------\n"
    )
    # Use formatted prints from https://stackoverflow.com/questions/10623727/python-spacing-and-aligning-strings
    stor_folder_labl = "Storage Folder"
    print(
        "{0:30}{1:30}{2}".format("Storage File", "Data Time Period", stor_folder_labl)
    )
    print("{0:30}{1:30}{2}".format("-" * 25, "-" * 25, "-" * len(stor_folder_labl)))

    dfs_with_data = 0
    successfully_stored_raw_data_files = []
    # Add the string version of the loop variable to exclude it from retrieve_variable_name().
    all_names_to_exclude = ["dataframe"]
    for timeframe in filing_dict:
        for dataframe in filing_dict[timeframe]:
            gt_file_name = store.retrieve_variable_name(dataframe, all_names_to_exclude)
            # After every name generation, append it to the exclude list.
            # That way, next time the script runs, it'll exclude variables that have already been named.
            # see https://github.com/ccaoa/google-ece-trends/issues/3.
            all_names_to_exclude.append(gt_file_name)
            if core.check_empty_dataframe(dataframe) is False:
                short_path = os.path.join(
                    "~",
                    os.path.split(os.path.split(os.path.split(storage_path)[0])[0])[1],
                    os.path.split(os.path.split(storage_path)[0])[1],
                    os.path.split(storage_path)[1],
                )
                successfully_stored_raw_data_file = store.store_data(
                    storage_path,
                    dataframe,
                    timeframe,
                    gtrends_file_name=gt_file_name,
                    csv_not_xlsx=True,
                    suppress_prints=True,
                )
                # print(str(gt_file_name)+'\t'+str(timeframe)+'\t\t'+str(short_path))
                # Use formatted prints from https://stackoverflow.com/questions/10623727/python-spacing-and-aligning-strings
                print("{0:30}{1:30}{2}".format(gt_file_name, timeframe, short_path))
                dfs_with_data += 1
                successfully_stored_raw_data_files.append(
                    successfully_stored_raw_data_file
                )
            else:
                # In the future, use some try loop to get all the data that were not collected originally to run again.
                print(
                    gt_file_name,
                    "was not captured and will not be stored.",
                )
    print(
        "\n-----------------------------------------------\n",
        # Print # of datasets stored out of total # datasets pulled.
        dfs_with_data,
        "out of",
        dfs_to_process,
        "datasets stored.\n-----------------------------------------------\n",
    )

    return successfully_stored_raw_data_files


def get_most_recent_files(path: str, num_files_to_keep: int) -> list:
    # Get a list of all files in the directory
    all_files = [os.path.join(path, filename) for filename in os.listdir(path)]

    # Sort files by modification time in descending order
    sorted_files = sorted(all_files, key=os.path.getmtime, reverse=True)

    # Choose the most recent files
    recent_files = sorted_files[:num_files_to_keep]

    return recent_files


def get_raw_files_by_date(target_date: str, path: str = None) -> list:
    """ Identify raw data files by the custom date input. Doesn't have to be the latest X number of files. """
    # Ensure right format for input variables
    if not path:
        path = storage_path
    target_date = str(target_date)

    # Define a pattern that matches files ending with a target date in yyyymmdd format
    date_pattern = re.compile(r".*_" + re.escape(target_date) + r"\.csv$")

    # Get a list of all files in the directory
    all_files = [os.path.join(path, filename) for filename in os.listdir(path)]

    # Filter files that match the date pattern
    matching_files = [file for file in all_files if date_pattern.match(file)]

    return matching_files


def append_and_summarize(list_of_raw_files: list):
    # Append the successfully pulled files into the corresponding raw data collection XLSX
    raw_data_collection_xlsxs = app.append_raw_data_from_files(
        list_of_raw_files, suppress_prints=False
    )
    sleep(2.5)
    # # Now re-run the summary statistics for the datasets that were successfully grabbed in this pull.
    # # # No sense in agg.summarize_all_summary_data() if some of those have no new data due to failures \
    # # # in the data collection phase. So only get the summary stats xlsx names for the data that did pull correctly.
    targ_aggfiles_listdir = [rdc for rdc in raw_data_collection_xlsxs]
    all_sum_fils_for_this_run = agg.summarize_collected_data(
        targ_aggfiles_listdir, suppress_prints=False
    )
    return all_sum_fils_for_this_run


def append_summarize_custom_date(custom_date_yyyymmdd, raw_data_pth:str = None):
    """ Use raw data from a single custom date and append them to the appropriate summary files."""
    targ_files = get_raw_files_by_date(target_date=custom_date_yyyymmdd, path=raw_data_pth)
    summed_files = append_and_summarize(targ_files)
    return summed_files


def append_summarize_custom_dates(custom_dates_list_yyyymmdd: list, raw_data_pth:str = None):
    """ Use raw data from multiple custom dates and append them to the appropriate summary files.
    This function is better for multiple custom dates because it only summarizes the appeneded data once
    as opposed to repeatedly doing so iteratively for each custom date."""
    all_targ_files = []
    for date in custom_dates_list_yyyymmdd:
        targ_files = get_raw_files_by_date(target_date=date, path=raw_data_pth)
        all_targ_files = all_targ_files + targ_files
    summed_files = append_and_summarize(all_targ_files)
    return summed_files


def full_run_gtrends(
    pull_trends_data: bool = True, low_search_volume_results: bool = True, number_of_raw_files: int = 23
):
    """Collect and summarize custom data for J. A. Cooper (2024) Google Trends publication."""
    pull_trends_data = core.string_to_bool(pull_trends_data)
    if pull_trends_data:
        # Collect the Google Trends Data by pulling it with the pytrends unofficial API.
        # # Custom function that pulls exactly what we need.
        successfully_stored_raw_data_files = full_gtrends_pull(
            core.string_to_bool(low_search_volume_results)
        )
    else:
        # Don't pull data again from Google. Default to the most recent files stored in the storage directory.
        # # This would be useful if the pull code runs successfully, but the summary code needs testing and bugfixing.
        # # This allows you to not re-hit the Google Trends API repeatedly during development. It is not the default.
        number_of_raw_files = int(number_of_raw_files)
        successfully_stored_raw_data_files = get_most_recent_files(
            storage_path, number_of_raw_files
        )
        # print(successfully_stored_raw_data_files)

        # Check to make sure they all have the same pull date
        unique_pull_dates = list(
            set([x[len(x) - 12 :] for x in successfully_stored_raw_data_files])
        )
        if len(unique_pull_dates) > 1:
            print("Raw data files from multiple pull dates selected for summarizing:")
            print(unique_pull_dates)
        elif len(unique_pull_dates) == 0:
            print("No raw data files to append")
            exit()
        else:
            # Should only trigger if len()==1
            print("Summarizing raw data files pulled on", unique_pull_dates[0])

    # Summarize the data you just pulled into the summary XLSX to find overall statistics about your Google Trends data.
    all_sum_fils_for_this_run = append_and_summarize(successfully_stored_raw_data_files)

    return all_sum_fils_for_this_run


if __name__ == "__main__":
    # from time import time
    start = time()

    # Regular full run: pull data, append it, and summarize it.
    full_run_gtrends(pull_trends_data=True)

    # # Append and summarize already pulled data.
    # # # Either identify this by the most recent X number of files:
    # number_raw_files = 23  # 23 files pulled daily as of Aug 2023.
    # full_run_gtrends(pull_trends_data=False, number_of_raw_files=number_raw_files)
    # # # Or, identify raw files by their date if they're not the most recent.
    # # # # Single custom date.
    # append_summarize_custom_date(20240911)
    # # # # Or, multiple custom dates.
    # append_summarize_custom_dates([20240616])

    # # Only summarize the already-appended data:
    # agg.summarize_all_appended_data(os.path.expanduser(r"~\NACCRRA\Research Team - Documents\Mapping\google_trends\gtrends_data\summary_data"))

    core.runtime(start=start)
