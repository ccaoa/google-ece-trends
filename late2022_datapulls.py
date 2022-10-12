import pandas as pd
from ccaoa import core
from time import time, sleep

try:
    from . import pull_data as pull, store_data as store
except:
    import pull_data as pull, store_data as store


def full_run_gtrends():
    """ """
    # Beware of timeout requests:
    # `pytrends.exceptions.ResponseError: The request failed: Google returned a response with code 429.`
    # https://stackoverflow.com/questions/50571317/pytrends-the-request-failed-google-returned-a-response-with-code-429
    google_connection = pull.connect_to_gtrends()
    sleep(11)  # >10 second pause to trick the Google API?

    # Establish a dictionary to contain the dataframes for downstream saving.
    filing_dict = {}
        # valentines_period: [valentines_states_df,valentines_temporal_df,valentines_dma_df,valentines_top_qs,valentines_rising_qs],
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
    #
    # Set up variables here for dynamic and multiple downstream uses.
    # # Set all future DF variables to None for now. They'll be defined later.
    usa_states_df = usa_temporal_df = usa_dma_df = usa_top_qs = usa_rising_qs =ky_dma = ky_time = in_dma = in_time = oh_dma = oh_time = None
    # # Put all these vars in a list.
    u_fil_list = [
        usa_states_df, usa_temporal_df, usa_dma_df, usa_top_qs, usa_rising_qs,
        ky_dma,ky_time,in_dma,in_time,oh_dma,oh_time,
    ]
    # # Now define their unique arguments for the extract_data() function.
    # # # Doing it here this way ensures that you can try running the function again if the first time does not work.
    # # # Dict template: {df: (payload_item, spatial_not_temporal=True, region=None, low_volume=True, suppress_prints=True}
    # # # # For payload_item, define its variables. Don't want to keep creating payloads (right?)

    #
    # Build the payload
    usa_payload = pull.payload_builder(timeframe=init_late2022_studyperiod, geography_broad=geog_usa, connection_item=google_connection)  # Default args  # Future: pass your timeframe argument into this func.
    sleep(11)  # >10 second pause to trick the Google API?
    #
    # Use the extract_data_try(payload_item, spatial_not_temporal=True, region=None, low_volume=True) func
    # to pull relevant data + formatting out of the payload.
    usa_states_df = pull.extract_data_try(usa_payload, region='states', spatial_not_temporal=True)
    sleep(11)  # >10 second pause to trick the Google API?
    usa_temporal_df = pull.extract_data_try(usa_payload, spatial_not_temporal=False)
    sleep(11)  # >10 second pause to trick the Google API?
    usa_dma_df = pull.extract_data_try(usa_payload, spatial_not_temporal=True,region='DMA')

    #
    # Get related queries
    usa_top_qs = pull.top_related_queries(usa_payload)
    sleep(11)  # >10 second pause to trick the Google API?
    usa_rising_qs = pull.rising_related_queries(usa_payload)

    # Collect data to highlight the Cincinnati Problem (The fact that DMAs are inconsistently reported at state level):
    geog_ky = 'US-KY'
    # Build the payloads
    # *NOTE: Looks like you can only have 1 payload active at a time. Do all calcs for KY, THEN move on to IN, etc!*
    # So, KY is up first.
    ky_payload = pull.payload_builder(geography_broad=geog_ky, timeframe=init_late2022_studyperiod, connection_item=google_connection)
    sleep(11)  # >10 second pause to trick the Google API?
    # Pull relevant data
    ky_dma = pull.extract_data_try(payload_item=ky_payload, spatial_not_temporal=True, region='DMA')
    sleep(21)
    ky_time = pull.extract_data_try(payload_item=ky_payload, spatial_not_temporal=False)
    sleep(11)
    #
    # Next is Indiana
    geog_in = 'US-IN'
    in_payload = pull.payload_builder(geography_broad=geog_in, timeframe=init_late2022_studyperiod, connection_item=google_connection)
    sleep(11)  # >10 second pause to trick the Google API?
    in_dma = pull.extract_data_try(payload_item=in_payload, spatial_not_temporal=True, region='DMA')
    sleep(11)
    in_time = pull.extract_data_try(payload_item=in_payload, spatial_not_temporal=False)
    sleep(11)
    #
    # Finally, Ohio
    geog_oh = 'US-OH'
    oh_payload = pull.payload_builder(geography_broad=geog_oh, timeframe=init_late2022_studyperiod, connection_item=google_connection)
    sleep(11)
    oh_dma = pull.extract_data_try(payload_item=oh_payload, spatial_not_temporal=True, region='DMA')
    sleep(11)
    oh_time = pull.extract_data_try(payload_item=oh_payload, spatial_not_temporal=False)
    sleep(21)

    # Filing dictionary work
    u_fil_list = [
        usa_states_df, usa_temporal_df, usa_dma_df, usa_top_qs, usa_rising_qs,
        ky_dma,ky_time,in_dma,in_time,oh_dma,oh_time,
    ]
    # Add each df collected to the filing dictionary
    [filing_dict[init_late2022_studyperiod].append(u) for u in u_fil_list]# if u not in filing_dict[init_late2022_studyperiod]]  # <- Causes errors https://stackoverflow.com/questions/18548370/pandas-can-only-compare-identically-labeled-dataframe-objects-error


    # Also include some data from the classic COVID Valentines' study period.
    # Augment the OR & MN data with some national spatial data + get some riding and top keywords.
    valentines_period = '2020-02-14 2021-02-14'
    filing_dict[valentines_period] = []  # Establish dictionary list for downstream filing.
    # Build the payload
    valentines_usa_payload = pull.payload_builder(valentines_period, geography_broad=geog_usa, connection_item=google_connection)
    sleep(11)  # >10 second pause to trick the Google API?
    valentines_states_df = pull.extract_data_try(valentines_usa_payload, region='states', spatial_not_temporal=True)
    sleep(11)  # >10 second pause to trick the Google API?
    valentines_temporal_df = pull.extract_data_try(valentines_usa_payload, spatial_not_temporal=False)
    sleep(11)  # >10 second pause to trick the Google API?
    valentines_dma_df = pull.extract_data_try(valentines_usa_payload, spatial_not_temporal=True,region='DMA')
    sleep(11)  # >10 second pause to trick the Google API?
    #
    # Get related queries
    valentines_top_qs = pull.top_related_queries(valentines_usa_payload)
    sleep(11)  # >10 second pause to trick the Google API?
    valentines_rising_qs = pull.rising_related_queries(valentines_usa_payload)
    # Filing dictionary work
    v_fil_list = [valentines_states_df,valentines_temporal_df,valentines_dma_df,valentines_top_qs,valentines_rising_qs]
    # Add each df collected to the filing dictionary
    [filing_dict[valentines_period].append(v) for v in v_fil_list]# if v not in filing_dict[valentines_period]]  # # <- Causes errors


    # NEXT: Store all the data for all of the dataframes generated here.
    #Example below:
    # storage_path = r"C:\Users\Jacob.Cooper\NACCRRA\Research Team - Documents\Mapping\google_trends"
    storage_path = r"C:\Users\acc-s\Documents\Coding\Git\GitHub\ccaoa_github\gtrends_data"
    #do it by making a dictionary {timeframe:[df1,df2],timeframe2:[df4,df5]}
    # Try adding each df to the dict after it is created above in the code.
    # # That way, if I comment out certain parts, it won't error here for having undefined variables.
    # filing_dict={
    #     valentines_period: [valentines_states_df,valentines_temporal_df,valentines_dma_df,valentines_top_qs,valentines_rising_qs],
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
    full_run_gtrends()
