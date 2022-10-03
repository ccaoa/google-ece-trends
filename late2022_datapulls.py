import pandas as pd
from ccaoa import core
from time import time, sleep

from . import pull_data as pull

def full_run_gtrends():
    """ """
    # Beware of timeout requests:
    # `pytrends.exceptions.ResponseError: The request failed: Google returned a response with code 429.`
    # https://stackoverflow.com/questions/50571317/pytrends-the-request-failed-google-returned-a-response-with-code-429

    # USA pulls
    # # Remember, the payload is where you pass your study time-period argument
    init_202210_studyperiod = '2020-02-14 2021-02-14'  # The COVID Valentines' study period.
    usa_payload = pull.payload_builder()  # Default args  # Future: pass your timeframe argument into this func.
    # Reformat the below with extract_data(payload_item, spatial_not_temporal=True, region=None, low_volume=True) func.
    sleep(2)  # 2 second pause to trick the Google API?
    usa_states_df = pull.extract_data(usa_payload, region='states', spatial_not_temporal=True)
    sleep(2)  # 2 second pause to trick the Google API?
    usa_temporal_df = pull.extract_data(usa_payload, spatial_not_temporal=False)
    sleep(2)  # 2 second pause to trick the Google API?
    usa_dma_df = pull.extract_data(usa_payload, spatial_not_temporal=True,region='DMA')

    # Also include some data from the classic COVID Valentines' study period.
    # Augment the OR & MN data with some national spatial data + get some riding and top keywords.
    valentines_period = '2020-02-14 2021-02-14'
    valentines_usa_payload = pull.payload_builder()
    return


if __name__ == '__main__':
    store_data()
