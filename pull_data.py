"""
___
Pulls heavily from:
* https://github.com/GeneralMills/pytrends
* https://github.com/Tanu-N-Prabhu/Python/blob/master/Google_Trends_API.ipynb
"""

import pandas as pd
from ccaoa import core
from pytrends.request import TrendReq

ece_topic_code = "%2Fm%2F022hpx".replace("%2F",r"/")


def connect_to_gtrends(language='en-US'):
    """ This is a shell function for pytrends.request.TrendReq().
    That function takes several arguments, but until they are better understood, the defaults will be used. """

    # LANGUAGE
    # Likely will need to flesh out this argument to dynamically select more than US English, but start with that.
    if 'english' in language.lower():
        language = 'en-US'

    # Connect to Google Trends; open the gateway.
    ptrend = TrendReq(
        hl='en-US',
        # tz=360, timeout=(10,25), retries=2, backoff_factor=0.1, requests_args={'verify':False} #,proxies=['https://34.203.233.13:80']}#
    )
    return ptrend



def payload_builder(timeframe=None, search_item=ece_topic_code,geography_broad='US', connection_item=None):
    """ The payload is the base parameter set that tells Google the broad picture of what you're trying to research:
    the 'What, Where, & When' of GTrends data pulls. 
    The 'When' is likely to be the most variable for CCAoA. Formatting this argument will likely take its own function. 
    What = the child care topic.
    Where = USA (while state specific searches could be used, you run the risk of the Cincinnati Problem). """

    # TIMEFRAME
    # https://github.com/GeneralMills/pytrends#interest-by-region:~:text=is%20%27360%27-,timeframe,-Date%20to%20start
    # Fully Formatting this argument will likely take creating its own function.
    # # Defaults to last 5yrs, 'today 5-y'
    # # Note Time component is based off UTC
    # Set a placeholder timeframe for now
    if timeframe is None:
        timeframe = '2020-02-14 2021-02-14'  # The COVID Valentines' study period.

    # SEARCH TERM, TOPIC, OR CATEGORY
    # Assume the prominently consistent search item is the topic of Child Care, "%2Fm%2F022hpx"
    # Don't use child care category. Returns insignificant results in browser, so maybe unreliable pytrends data.
    # # 403 is the Child Care category, but that's not returning much.
    # Instead, search for the Child care "Topic", what has been used for initial research.
    # You can search for topics by following this methodology: https://github.com/GeneralMills/pytrends/issues/437
    # It must be translated to (see issue link above):
    search_item = search_item.replace("%2F", r"/")

    # GEOGRAPHY
    # Set up framework here for if a user passes a state to transform it into the correct format for the payload build.
    usa_list = ["USA","US","UNITEDSTATES", 'AMERICA']
    if geography_broad.replace(" ",'').upper() not in usa_list:
        geography_broad= core.st_upperformat(geography_broad)
    else:
        geography_broad = 'US'

    # Build the payload
    if connection_item is None:
        connection_item=connect_to_gtrends()
    connection_item.build_payload(kw_list=[search_item],timeframe=timeframe,geo=geography_broad)

    return connection_item


# Now, from a built payload, you can extract all sorts of stuff by accessing properties of the payload variable.
#     # Probably the most popular will be spatial and temporal.
#     # payload.interest_over_time()  # Temporal
#     # payload.interest_by_region()  # Spatial
#     # payload.related_topics()
#     # payload.related_queries()
#     # payload.get_historical_interest(keywords)

def extract_temporal_data(payload=None):
    """ Pass a connection item with a built payload into this function to extract meaningful time data from it. """

    if payload is None:
        payload=payload_builder()

    # Pull the time data for the payload parameters
    time_df = payload.interest_over_time()
    #
    # Format the new DF to make it easier to read
    time_df=time_df.rename(columns={ece_topic_code: "gtis"})

    return time_df


def extract_spatial_data(payload=None,subregion="REGION", low_volume=True):
    """ Pass a connection item with a built payload into this function to extract meaningful geography data from it.
    This will look at Trends across Sub-Geographies as Units of Analysis (UOAs)"""

    if payload is None:
        payload=payload_builder()

    # Determine which subregion is to be examined.
    # The default is "REGION", the international code for subnational UOAs (Admin Level 1).
    # # For the US, this is States.
    # However, useful also in the US are media markets, specifically Nielsen Designated Market Areas (DMAs).
    # # This is the last continuous geography in the USA.
    # Finally, there are cities. 'CITY' returns city level data
    # 'COUNTRY' returns country level data. In case you wanted one score for the whole US?
    uoa_resolutions =['COUNTRY','REGION','DMA','CITY']
    if subregion.upper().replace(" ","") not in uoa_resolutions:
        print("Your entered geography value", subregion, "was not valid; defaulting to State analysis.")
        subregion='REGION'

    # Do we want to include geographies with low volumes of searches?
    # # Default is yes.
    low_volume = core.string_to_bool(low_volume)

    # Pull the time data for the payload parameters
    geog_df = payload.interest_by_region(resolution=subregion, inc_low_vol=low_volume)
    #
    # Format the new DF to make it easier to read
    geog_df=geog_df.rename(columns={ece_topic_code: "gtis"})

