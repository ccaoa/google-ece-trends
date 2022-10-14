import pandas as pd, os
from ccaoa import core
from time import time, sleep
from pathlib import Path

try:
    from . import pull_data as pull, store_data as store, dma
except:
    import pull_data as pull, store_data as store, dma


def get_storage_path():
    """ Dynamically define the storage path with an external file that you gitignore.
    Keeps one from having to constantly edit their file paths in-code if working on different machines."""
    dot_storage_path = os.path.join(os.path.curdir,".storage_path")
    if not os.path.exists(dot_storage_path):
        Path(dot_storage_path).touch()
    with open(dot_storage_path) as sfile:
        path_store = str(sfile.read())
    # Make sure there are no pythonic quotations, etc around the path.
    path_store=path_store.replace('r"','"').replace('"','')
    if not os.path.exists(path_store):
        print("Your file",
              path_store,
              "doesn't exist.\n"
              "Edit your `.storage_path` file in this directory to designate a destination for the Google Trends data.")
        # # Maybe in a future version, add a user input method to manually define this var in-run.
    sfile.close()
    return path_store


def full_run_gtrends():
    """ Collect custom data for J. A. Cooper (2023) Google Trends publication. """
    # Make sure you have a valid storage location before going to the trouble of running all these trends.
    storage_path = get_storage_path()
    if storage_path is None or storage_path == '':
        # Cancel out of the run early; there's nowhere to store the data, so no use in continuing till you have that.
        return

    # Beware of timeout requests:
    # `pytrends.exceptions.ResponseError: The request failed: Google returned a response with code 429.`
    # https://stackoverflow.com/questions/50571317/pytrends-the-request-failed-google-returned-a-response-with-code-429
    google_connection = pull.connect_to_gtrends(retries=8, backoff_factor=.7)
    # sleep(11)  # >10 second pause to trick the Google API?

    # Establish a dictionary to contain the dataframes for downstream saving.
    filing_dict = {}
        # valentines_time_period: [valentines_states_df,valentines_temporal_df,valentines_dma_df,valentines_top_qs,valentines_rising_qs],
        # init_late2022_studyperiod:[
        #     usa_states_df,usa_temporal_df,usa_dma_df,usa_top_qs,usa_rising_qs,
        #     ky_dma,ky_time,in_dma,in_time,oh_dma,oh_time,
        # ]
    # }

    # USA pulls
    # # Remember, the payload is where you pass your study time-period argument
    init_late2022_studyperiod = '2018-06-03 2022-09-10'  # The COVID Valentines' study period.
    filing_dict[init_late2022_studyperiod]=[]  # Establish dictionary list for downstream filing.
    geog_usa = 'US'
    # Build the payload
    usa_payload = pull.payload_builder(timeframe=init_late2022_studyperiod, geography_broad=geog_usa, connection_item=google_connection)  # Default args  # Future: pass your timeframe argument into this func.
    # sleep(11)  # >10 second pause to trick the Google API?
    #
    # Use the extract_data_try(payload_item, spatial_not_temporal=True, region=None, low_volume=True) func
    # to pull relevant data + formatting out of the payload.
    usa_states_df = pull.extract_data_try(usa_payload, region='states', spatial_not_temporal=True)
    # # sleep(11)  # >10 second pause to trick the Google API?
    usa_temporal_df = pull.extract_data_try(usa_payload, spatial_not_temporal=False)
    # # sleep(11)  # >10 second pause to trick the Google API?
    usa_dma_df = pull.extract_data_try(usa_payload, spatial_not_temporal=True,region='DMA')

    #
    # Get related queries
    usa_top_qs = pull.top_related_queries(usa_payload)
    # # sleep(11)  # >10 second pause to trick the Google API?
    usa_rising_qs = pull.rising_related_queries(usa_payload)

    # Collect data to highlight the Cincinnati Problem (The fact that DMAs are inconsistently reported at state level):
    geog_ky = 'US-KY'
    # Build the payloads
    # *NOTE: Looks like you can only have 1 payload active at a time. Do all calcs for KY, THEN move on to IN, etc!*
    # So, KY is up first.
    ky_payload = pull.payload_builder(geography_broad=geog_ky, timeframe=init_late2022_studyperiod, connection_item=google_connection)
    # sleep(11)  # >10 second pause to trick the Google API?
    # Pull relevant data
    ky_dma = pull.extract_data_try(payload_item=ky_payload, spatial_not_temporal=True, region='DMA')
    # sleep(11)
    ky_time = pull.extract_data_try(payload_item=ky_payload, spatial_not_temporal=False)
    # sleep(11)
    #
    # Next is Indiana
    geog_in = 'US-IN'
    in_payload = pull.payload_builder(geography_broad=geog_in, timeframe=init_late2022_studyperiod, connection_item=google_connection)
    # sleep(11)  # >10 second pause to trick the Google API?
    in_dma = pull.extract_data_try(payload_item=in_payload, spatial_not_temporal=True, region='DMA')
    # sleep(11)
    in_time = pull.extract_data_try(payload_item=in_payload, spatial_not_temporal=False)
    # sleep(11)
    #
    # Finally, Ohio
    geog_oh = 'US-OH'
    oh_payload = pull.payload_builder(geography_broad=geog_oh, timeframe=init_late2022_studyperiod, connection_item=google_connection)
    # sleep(11)
    oh_dma = pull.extract_data_try(payload_item=oh_payload, spatial_not_temporal=True, region='DMA')
    # sleep(11)
    oh_time = pull.extract_data_try(payload_item=oh_payload, spatial_not_temporal=False)
    # sleep(11)

    # Filing dictionary work
    u_fil_list = [
        usa_states_df, usa_temporal_df, usa_dma_df, usa_top_qs, usa_rising_qs,
        ky_dma,ky_time,in_dma,in_time,oh_dma,oh_time,
    ]
    # Add each df collected to the filing dictionary
    [filing_dict[init_late2022_studyperiod].append(u) for u in u_fil_list]# if u not in filing_dict[init_late2022_studyperiod]]  # <- Causes errors https://stackoverflow.com/questions/18548370/pandas-can-only-compare-identically-labeled-dataframe-objects-error


    # Also include some data from the classic COVID Valentines' study period.
    # Augment the existing OR & MN data with some national spatial data + get some riding and top keywords.
    valentines_time_period = '2020-02-14 2021-02-14'
    filing_dict[valentines_time_period] = []  # Establish dictionary list for downstream filing.
    # Build the payload
    valentines_usa_payload = pull.payload_builder(valentines_time_period, geography_broad=geog_usa, connection_item=google_connection)
    # sleep(11)  # >10 second pause to trick the Google API?
    valentines_states_df = pull.extract_data_try(valentines_usa_payload, region='states', spatial_not_temporal=True)
    # sleep(11)  # >10 second pause to trick the Google API?
    valentines_temporal_df = pull.extract_data_try(valentines_usa_payload, spatial_not_temporal=False)
    # sleep(11)  # >10 second pause to trick the Google API?
    valentines_dma_df = pull.extract_data_try(valentines_usa_payload, spatial_not_temporal=True,region='DMA')
    # sleep(11)  # >10 second pause to trick the Google API?
    #
    # Get related queries
    valentines_top_qs = pull.top_related_queries(valentines_usa_payload)
    # sleep(11)  # >10 second pause to trick the Google API?
    valentines_rising_qs = pull.rising_related_queries(valentines_usa_payload)
    #
    # Pull state-level OR & MN data to demonstrate how the Cincy Problem has been resolved by Google
    # # since March - April 2021 when original MN & OR data was collected.
    # 1st, MN
    geog_mn = 'US-MN'
    mn_payload = pull.payload_builder(geography_broad=geog_mn, timeframe=valentines_time_period,
                                      connection_item=google_connection)
    mn_dma = pull.extract_data_try(payload_item=mn_payload, spatial_not_temporal=True, region='DMA')
    mn_time = pull.extract_data_try(payload_item=mn_payload, spatial_not_temporal=False)
    # Then, Oregon
    geog_or = 'US-OR'
    or_payload = pull.payload_builder(geography_broad=geog_or, timeframe=valentines_time_period,
                                      connection_item=google_connection)
    or_dma = pull.extract_data_try(payload_item=or_payload, spatial_not_temporal=True, region='DMA')
    or_time = pull.extract_data_try(payload_item=or_payload, spatial_not_temporal=False)
    # Also include Eugene, Oregon to look within a DMA for kicks and longitudinal consistency.
    # # The Beaver/Duck DMA!
    # To construct the geography, we need that DMA ID. Dynamically access it.
    beaver_duck_dma_name = next(key for key in core.reverse_dict(dma.dma_id_dict()) if "Eugene" in key)
    beaver_duck_dma_id = str(core.reverse_dict(dma.dma_id_dict())[beaver_duck_dma_name])
    geog_eugene = geog_or + "-" + beaver_duck_dma_id
    # Then, go on collecting data like normal.
    eugene_payload = pull.payload_builder(geography_broad=geog_eugene, timeframe=valentines_time_period,connection_item=google_connection)
    eugene_time = pull.extract_data_try(payload_item=eugene_payload, spatial_not_temporal=False)
    # A City-level UOA pull!
    eugene_city = pull.extract_data_try(payload_item=eugene_payload, spatial_not_temporal=True, region='city')
    #
    # Filing dictionary work
    v_fil_list = [valentines_states_df,valentines_temporal_df,valentines_dma_df,valentines_top_qs,valentines_rising_qs,
                  mn_dma,mn_time, or_dma, or_time, eugene_time, eugene_city]
    # Add each df collected to the filing dictionary
    [filing_dict[valentines_time_period].append(v) for v in v_fil_list]# if v not in filing_dict[valentines_time_period]]  # # <- Causes errors


    # NEXT: Store all the data for all of the dataframes generated here.
    #Example below:
    # Storage paths now dynamically set.
    # storage_path = r"C:\Users\Jacob.Cooper\NACCRRA\Research Team - Documents\Mapping\google_trends"
    # storage_path = r"C:\Users\acc-s\Documents\Coding\Git\GitHub\ccaoa_github\gtrends_data"
    #do it by making a dictionary {timeframe:[df1,df2],timeframe2:[df4,df5]}
    # Try adding each df to the dict after it is created above in the code.
    # # That way, if I comment out certain parts, it won't error here for having undefined variables.
    # filing_dict={
    #     valentines_time_period: [valentines_states_df,valentines_temporal_df,valentines_dma_df,valentines_top_qs,valentines_rising_qs],
    #     init_late2022_studyperiod:[
    #         usa_states_df,usa_temporal_df,usa_dma_df,usa_top_qs,usa_rising_qs,
    #         ky_dma,ky_time,in_dma,in_time,oh_dma,oh_time,
    #     ]
    # }
    #then   for tf in dict: for df in tf: store_data().
    # store.store_data(storage_path, usa_states_df,init_late2022_studyperiod)
    # store_data(storage_directory_file_path,gtrends_data, search_date_period, csv_not_xlsx=True)
    print("Data will be stored in", storage_path,'\n-----------------------------------------------')
    # Set the stage for reprocessing previously failed data collection efforts.
    dfs_to_process=0
    # Count all the DFs to process
    for tf in filing_dict:
        dfs_to_process += len(filing_dict[tf])
    dfs_with_data = 0
    # while dfs_to_process > dfs_with_data:  # Eventually use this for retrying previously failed datasets.
    for tf in filing_dict:
        for dataframe in filing_dict[tf]:
            if core.check_empty_dataframe(dataframe) is False:
                store.store_data(storage_path,dataframe,tf,gtrends_file_name=store.retrieve_singlevar_name(dataframe),csv_not_xlsx=True)
                dfs_with_data+=1
                print(store.retrieve_singlevar_name(dataframe),"was stored for time period", tf)
            else:
                # In the future, use some try loop to get all the data that were not collected originally to run again.
                print(store.retrieve_singlevar_name(dataframe),"was not captured and will not be stored.")
    print(dfs_with_data, "out of",dfs_to_process,'datasets stored.\n-----------------------------------------------\n')
    return


if __name__ == '__main__':
    start = time()
    full_run_gtrends()
    core.runtime(start=start)
