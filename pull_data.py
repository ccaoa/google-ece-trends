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


def payload_builder(timeframe=None, geography_broad='US', search_item=ece_topic_code, connection_item=None):
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
        # Thinking defining the timeframe outside of this function will be wise. Too much nesting otherwise.
        payload=payload_builder()

    # Pull the time data for the payload parameters
    time_df = payload.interest_over_time()
    #
    # Format the new DF to make it easier to read
    time_df=time_df.rename(columns={ece_topic_code: "gtis"})

    # The region item is set by default as a pandas DF index. We want it as an actual column.
    date_column = 'date'
    # Add the geog index as a column to the df
    time_df[date_column] = time_df.index
    # Move geog col as first column
    timecolumns = time_df.columns.to_list()
    timecolumns = timecolumns[-1:] + timecolumns[:-1]
    time_df = time_df[timecolumns]
    # Reset the index to be numerical.
    time_df = time_df.reset_index(drop=True)
    # Set the date column as the first in the df
    time_df = time_df[[date_column] + [col for col in time_df.columns if col != date_column]]

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
        if subregion.lower().replace(" ","") in ['state','states','usstates']:
            subregion = 'REGION'
        elif subregion.lower().replace(" ","") in ['county','counties']:
            print("Counties are not tracked by Google Trends. "
                  "The closest you can get for sub-state data is media markets.\n"
                  "Returning data for media markets.")
            subregion = 'DMA'
        else:
            print("Your entered geography value", subregion, "was not valid; defaulting to State analysis.")
            subregion='REGION'

    # Do we want to include geographies with low volumes of searches?
    # # Default is yes.
    low_volume = core.string_to_bool(low_volume)

    # ! Pull the trends data for the payload parameters
    geog_df = payload.interest_by_region(resolution=subregion, inc_low_vol=low_volume)

    # Format the new DF to make it easier to read
    score_column_name = 'gtis'
    geog_df=geog_df.rename(columns={ece_topic_code: score_column_name})
    # The region item is set by default as a pandas DF index. We want it as an actual column.
    region_column = subregion.lower()
    if region_column=='region':
        region_column='state'
    # Add the geog index as a column to the df
    geog_df[region_column] = geog_df.index
    # Move geog col as first column
    colsreg = geog_df.columns.to_list()
    colsreg = colsreg[-1:] + colsreg[:-1]
    geog_df = geog_df[colsreg]
    # Reset the index to be numerical.
    geog_df = geog_df.reset_index(drop=True)
    # We also want the regions in the df to have a rank
    # # Generate a plain, functional DF with a ranking of 1 to n(columns in region DF)
    rank_col = "rank"
    rank_df = pd.DataFrame(list(range(1, len(geog_df))), columns=[rank_col])
    geog_df = pd.concat(
        # Sorted version of the GTrends Data
        [geog_df.sort_values(score_column_name, ascending=False).reset_index(drop=True),
         # Merged with a ranking
         rank_df.astype(int)]
        , axis=1
    )
    del rank_df  # Take the scratch rank dataframe out of memory.
    # Set the date column as the first in the df
    geog_df = geog_df[[rank_col] + [col for col in geog_df.columns if col != rank_col]]


    return geog_df


if __name__ == '__main__':
    import time
    start = time.time()

    # Beware of timeout requests:
    # `pytrends.exceptions.ResponseError: The request failed: Google returned a response with code 429.`
    # https://stackoverflow.com/questions/50571317/pytrends-the-request-failed-google-returned-a-response-with-code-429
    payload = payload_builder()  # Default args  # Future: pass your timeframe argument into this func.
    states_df = extract_spatial_data(payload, subregion='states')
    temporal_df = extract_temporal_data()

    print(states_df.head(10))
    print(temporal_df.head(10))

    core.runtime(start)
