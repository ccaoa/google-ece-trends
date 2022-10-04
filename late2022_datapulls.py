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
    # USA pulls
    # # Remember, the payload is where you pass your study time-period argument
    init_late2022_studyperiod = '2018-06-03 2022-09-10'  # The COVID Valentines' study period.
    geog_usa = 'US'
    # Build the payload
    usa_payload = pull.payload_builder(timeframe=init_late2022_studyperiod, geography_broad=geog_usa, connection_item=google_connection)  # Default args  # Future: pass your timeframe argument into this func.
    sleep(2)  # 2 second pause to trick the Google API?
    #
    # Use the extract_data(payload_item, spatial_not_temporal=True, region=None, low_volume=True) func
    # to pull relevant data + formatting out of the payload.
    usa_states_df = pull.extract_data(usa_payload, region='states', spatial_not_temporal=True)
    sleep(2)  # 2 second pause to trick the Google API?
    usa_temporal_df = pull.extract_data(usa_payload, spatial_not_temporal=False)
    sleep(2)  # 2 second pause to trick the Google API?
    usa_dma_df = pull.extract_data(usa_payload, spatial_not_temporal=True,region='DMA')
    sleep(2)  # 2 second pause to trick the Google API?
    #
    # Get related queries
    usa_top_qs = pull.top_related_queries(usa_payload)
    usa_rising_qs = pull.rising_related_queries(usa_payload)

    # Collect data to highlight the Cincinnati Problem (The fact that DMAs are inconsistently reported at state level):
    geog_ky = 'US-KY'
    geog_in = 'US-IN'
    geog_oh = 'US-OH'
    # Build the payloads
    ky_payload = pull.payload_builder(geography_broad=geog_ky, timeframe=init_late2022_studyperiod, connection_item=google_connection)
    sleep(2)  # 2 second pause to trick the Google API?
    in_payload = pull.payload_builder(geography_broad=geog_in, timeframe=init_late2022_studyperiod, connection_item=google_connection)
    sleep(2)  # 2 second pause to trick the Google API?
    oh_payload = pull.payload_builder(geography_broad=geog_oh, timeframe=init_late2022_studyperiod, connection_item=google_connection)
    sleep(2)
    #
    # Pull relevant data
    ky_dma = pull.extract_data(payload_item=ky_payload, spatial_not_temporal=True, region='DMA')
    sleep(2)
    ky_time = pull.extract_data(payload_item=ky_payload, spatial_not_temporal=True)
    sleep(2)
    in_dma = pull.extract_data(payload_item=in_payload, spatial_not_temporal=True, region='DMA')
    sleep(2)
    in_time = pull.extract_data(payload_item=in_payload, spatial_not_temporal=True)
    sleep(2)
    oh_dma = pull.extract_data(payload_item=oh_payload, spatial_not_temporal=True, region='DMA')
    sleep(2)
    oh_time = pull.extract_data(payload_item=oh_payload, spatial_not_temporal=True)
    sleep(2)


    # Also include some data from the classic COVID Valentines' study period.
    # Augment the OR & MN data with some national spatial data + get some riding and top keywords.
    sleep(2)  # 2 second pause to trick the Google API?
    valentines_period = '2020-02-14 2021-02-14'
    # Build the payload
    valentines_usa_payload = pull.payload_builder(valentines_period, geography_broad=geog_usa, connection_item=google_connection)
    valentines_states_df = pull.extract_data(valentines_usa_payload, region='states', spatial_not_temporal=True)
    sleep(2)  # 2 second pause to trick the Google API?
    valentines_temporal_df = pull.extract_data(valentines_usa_payload, spatial_not_temporal=False)
    sleep(2)  # 2 second pause to trick the Google API?
    valentines_dma_df = pull.extract_data(valentines_usa_payload, spatial_not_temporal=True,region='DMA')
    sleep(2)  # 2 second pause to trick the Google API?
    #
    # Get related queries
    valentines_top_qs = pull.top_related_queries(valentines_usa_payload)
    valentines_rising_qs = pull.rising_related_queries(valentines_usa_payload)


    # NEXT: Store all the data for all of the dataframes generated here.
    #Example below:
    storage_path = r"C:\Users\Jacob.Cooper\NACCRRA\Research Team - Documents\Mapping\google_trends"
    store.store_data(storage_path, usa_states_df,init_late2022_studyperiod)
    #do it by making a dictionary {timeframe:[df1,df2],timeframe2:[df4,df5]}  then   for tf in dict: for df in tf: store_data().

    return


if __name__ == '__main__':
    full_run_gtrends()
