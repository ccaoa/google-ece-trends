import pandas as pd, os
from ccaoa import core
from time import time, sleep
from pathlib import Path

try:
    from . import pull_data as pull, store_data as store
except:
    import pull_data as pull, store_data as store


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
    sfile.close()
    return path_store


def full_run_gtrends():
    """ Collect custom data for J. A. Cooper (2023) Google Trends publication. """
    # Make sure you have a valid storage location before going to the trouble of running all these trends.
    storage_path = get_storage_path()

    # Beware of timeout requests:
    # `pytrends.exceptions.ResponseError: The request failed: Google returned a response with code 429.`
    # https://stackoverflow.com/questions/50571317/pytrends-the-request-failed-google-returned-a-response-with-code-429
    google_connection = pull.connect_to_gtrends()
    sleep(11)  # >10 second pause to trick the Google API?

    # USA pulls
    # # Remember, the payload is where you pass your study time-period argument
    init_late2022_studyperiod = '2018-06-03 2022-09-10'  # The COVID Valentines' study period.
    geog_usa = 'US'
    # Build the payload
    usa_payload = pull.payload_builder(timeframe=init_late2022_studyperiod, geography_broad=geog_usa, connection_item=google_connection)  # Default args  # Future: pass your timeframe argument into this func.
    sleep(11)  # >10 second pause to trick the Google API?
    #
    # Use the extract_data(payload_item, spatial_not_temporal=True, region=None, low_volume=True) func
    # to pull relevant data + formatting out of the payload.
    usa_states_df = pull.extract_data(usa_payload, region='states', spatial_not_temporal=True)
    sleep(11)  # >10 second pause to trick the Google API?
    usa_temporal_df = pull.extract_data(usa_payload, spatial_not_temporal=False)
    sleep(11)  # >10 second pause to trick the Google API?
    usa_dma_df = pull.extract_data(usa_payload, spatial_not_temporal=True,region='DMA')
    sleep(11)  # >10 second pause to trick the Google API?
    #
    # Get related queries
    usa_top_qs = pull.top_related_queries(usa_payload)
    usa_rising_qs = pull.rising_related_queries(usa_payload)

    # Collect data to highlight the Cincinnati Problem (The fact that DMAs are inconsistently reported at state level):
    geog_ky = 'US-KY'
    # Build the payloads
    # *NOTE: Looks like you can only have 1 payload active at a time. Do all calcs for KY, THEN move on to IN, etc!*
    # So, KY is up first.
    ky_payload = pull.payload_builder(geography_broad=geog_ky, timeframe=init_late2022_studyperiod, connection_item=google_connection)
    sleep(11)  # >10 second pause to trick the Google API?
    # Pull relevant data
    ky_dma = pull.extract_data(payload_item=ky_payload, spatial_not_temporal=True, region='DMA')
    sleep(21)
    ky_time = pull.extract_data(payload_item=ky_payload, spatial_not_temporal=False)
    sleep(11)
    #
    # Next is Indiana
    geog_in = 'US-IN'
    in_payload = pull.payload_builder(geography_broad=geog_in, timeframe=init_late2022_studyperiod, connection_item=google_connection)
    sleep(11)  # >10 second pause to trick the Google API?
    in_dma = pull.extract_data(payload_item=in_payload, spatial_not_temporal=True, region='DMA')
    sleep(11)
    in_time = pull.extract_data(payload_item=in_payload, spatial_not_temporal=False)
    sleep(11)
    #
    # Finally, Ohio
    geog_oh = 'US-OH'
    oh_payload = pull.payload_builder(geography_broad=geog_oh, timeframe=init_late2022_studyperiod, connection_item=google_connection)
    sleep(11)
    oh_dma = pull.extract_data(payload_item=oh_payload, spatial_not_temporal=True, region='DMA')
    sleep(11)
    oh_time = pull.extract_data(payload_item=oh_payload, spatial_not_temporal=False)
    sleep(11)


    # Also include some data from the classic COVID Valentines' study period.
    # Augment the OR & MN data with some national spatial data + get some riding and top keywords.
    valentines_period = '2020-02-14 2021-02-14'
    # Build the payload
    valentines_usa_payload = pull.payload_builder(valentines_period, geography_broad=geog_usa, connection_item=google_connection)
    sleep(11)  # >10 second pause to trick the Google API?
    valentines_states_df = pull.extract_data(valentines_usa_payload, region='states', spatial_not_temporal=True)
    sleep(11)  # >10 second pause to trick the Google API?
    valentines_temporal_df = pull.extract_data(valentines_usa_payload, spatial_not_temporal=False)
    sleep(11)  # >10 second pause to trick the Google API?
    valentines_dma_df = pull.extract_data(valentines_usa_payload, spatial_not_temporal=True,region='DMA')
    sleep(11)  # >10 second pause to trick the Google API?
    #
    # Get related queries
    valentines_top_qs = pull.top_related_queries(valentines_usa_payload)
    valentines_rising_qs = pull.rising_related_queries(valentines_usa_payload)


    # NEXT: Store all the data for all of the dataframes generated here.
    #Example below:
    # storage_path = r"C:\Users\Jacob.Cooper\NACCRRA\Research Team - Documents\Mapping\google_trends"
    # storage_path = r"C:\Users\acc-s\Documents\Coding\Git\GitHub\ccaoa_github\gtrends_data"
    # Storage paths now dynamically set.
    #do it by making a dictionary {timeframe:[df1,df2],timeframe2:[df4,df5]}
    # Try adding each df to the dict after it is created above in the code.
    # # That way, if I comment out certain parts, it won't error here for having undefined variables.
    filing_dict={
        valentines_period: [valentines_states_df,valentines_temporal_df,valentines_dma_df,valentines_top_qs,valentines_rising_qs],
        init_late2022_studyperiod:[
            usa_states_df,usa_temporal_df,usa_dma_df,usa_top_qs,usa_rising_qs,
            ky_dma,ky_time,in_dma,in_time,oh_dma,oh_time,
        ]
    }
    #then   for tf in dict: for df in tf: store_data().
    # store.store_data(storage_path, usa_states_df,init_late2022_studyperiod)
    # store_data(storage_directory_file_path,gtrends_data, search_date_period, csv_not_xlsx=True)
    print("Data will be stored in", storage_path,'\n-----------------------------------------------')
    for tf in filing_dict:
        for dataframe in filing_dict[tf]:
            if core.check_empty_dataframe(dataframe) is False:
                store.store_data(storage_path,dataframe,tf,gtrends_file_name=store.retrieve_singlevar_name(dataframe),csv_not_xlsx=True)
                print(store.retrieve_singlevar_name(dataframe),"was stored for time period", tf)
            else:
                print(store.retrieve_singlevar_name(dataframe),"was not captured and will not be stored.")
    print('-----------------------------------------------\n')
    return


if __name__ == '__main__':
    full_run_gtrends()
