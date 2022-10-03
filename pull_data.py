"""
___
Pulls heavily from:
* https://github.com/GeneralMills/pytrends
* https://github.com/Tanu-N-Prabhu/Python/blob/master/Google_Trends_API.ipynb
"""

import pandas as pd
from ccaoa import core
import pytrends, os, inspect, json
from pytrends.request import TrendReq

ece_topic_code = "%2Fm%2F022hpx".replace("%2F", r"/")
worker_topic_code = "%2Fg%2F11bc6xhvhf".replace("%2F", r"/")


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
        statesearch = core.st_upperformat(geography_broad).replace('US-','')
        if statesearch in core.statedict():
            if statesearch=='DC':
                # DC is not considered an admin 1 by GTrends but an Admin 2 (DMA).
                geography_broad="US-MD-511"
            else:
                geography_broad = "US-"+statesearch
        # Eventually add options to drill into DMAs themselves. Use the state_dma_dict.
        else:
            # Default to the entire USA
            geography_broad = 'US'
    else:
        # Default to the entire USA
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


def gtis_df_formatter(payload_df, search_term, uoa, rank_sort=True):
    """ Generates a clean DF with a formatted GTIS column for either time or geography results
    with an optional ranking column for each UOA region. """

    # Rename the Google Trends Interest Score (GTIS) column
    score_column_name = 'gtis'
    payload_df =payload_df.rename(columns={search_term: score_column_name})
    # The date/geography variable item is set by default as a pandas DF index. We want it as an actual, physical column.
    # # If temporal, UOA should be = 'date'
    # # # (See if this differs as time period for results differs. I.e. if UOA is a week vs a day). If it does, see spatial function way of resolving multiple possible UOAs.
    # # If spatial, UOA will vary: uoa_resolutions =['COUNTRY','REGION','DMA','CITY']
    payload_df[uoa] = payload_df.index
    # Set UOA col as first column
    cols = payload_df.columns.to_list()
    cols = cols[-1:] + cols[:-1]
    payload_df = payload_df[cols]
    # Reset the index to be numerical.
    payload_df = payload_df.reset_index(drop=True)

    # Add a rank to the dataframe. Only sort if geography.
    # if rank is True:
    rank_dataframe = pd.DataFrame(list(range(1,len(payload_df)+1)), columns=['rank'])
    # Include the rankings in the payload dictionary
    if rank_sort is True:
        payload_df = pd.concat(
            # Sorted version of the GTrends Data
            [payload_df.sort_values(score_column_name, ascending=False).reset_index(drop=True),
             # Merge regional data with its GTIS ranking
             rank_dataframe]#.astype(int)]  # Strangely, setting astype to int gives it a decimal...
            , axis=1
        )
    else:
        # Rank results without sorting.
        dfforrank = pd.concat(
            # Sorted version of the GTrends Data
            # # Don't reset the index. Generates its own 'index' column to reference later.
            [payload_df.sort_values(score_column_name, ascending=False).reset_index(False),
             # Merge regional data with its GTIS ranking
             rank_dataframe]#.astype(int)]
            , axis=1
        )
        # Get your DF in it's OG order again.
        dfforrank = dfforrank.sort_values('index', ascending=True)
        # payload_df = dfforrank.drop('index')
        payload_df = dfforrank.set_index('index')
        del dfforrank

    del rank_dataframe

    # Set the UOA column as the first in the df
    payload_df = payload_df[[uoa] + [col for col in payload_df.columns if col != uoa]]

    return payload_df


def extract_temporal_data(payload=None, time_uoa='date'):
    """ Pass a connection item with a built payload into this function to extract meaningful time data from it. """

    if payload is None:
        # Thinking defining the timeframe outside of this function will be wise. Too much nesting otherwise.
        payload=payload_builder()

    # Pull the time data for the payload parameters
    time_df = payload.interest_over_time()
    #
    # Format the new DF to make it easier to read
    time_df = gtis_df_formatter(time_df, ece_topic_code, time_uoa, rank_sort=False)

    return time_df


def subregion_identifier(subregion_input):
    """ Figure out what sub-region of your broad geography you want to explore from the payload."""
    # The default is "REGION", the international code for subnational UOAs (Admin Level 1).
    # # For the US, this is States.
    # However, useful also in the US are media markets, specifically Nielsen Designated Market Areas (DMAs).
    # # This is the last continuous geography in the USA.
    # Finally, there are cities. 'CITY' returns city level data
    # 'COUNTRY' returns country level data. In case you wanted one score for the whole US?
    uoa_resolutions = ['COUNTRY', 'REGION', 'DMA', 'CITY']
    if subregion_input.upper().replace(" ", "") not in uoa_resolutions:
        if subregion_input.lower().replace(" ", "") in ['state', 'states', 'usstates']:
            subregion = 'REGION'
        elif subregion_input.lower().replace(" ", "") in ['county', 'counties']:
            print("Counties are not tracked by Google Trends. "
                  "The closest you can get for sub-state data is media markets.\n"
                  "Returning data for media markets.")
            subregion = 'DMA'
        else:
            print("Your entered geography value", subregion_input, "was not valid; defaulting to State analysis.")
            subregion = 'REGION'
    else:
        subregion = subregion_input

    return subregion


def extract_spatial_data(payload=None,subregion="REGION", low_volume=True):
    """ Pass a connection item with a built payload into this function to extract meaningful geography data from it.
    This will look at Trends across Sub-Geographies as Units of Analysis (UOAs)"""

    if payload is None:
        payload=payload_builder()

    # Determine which subregion is to be examined.
    subregion = subregion_identifier(subregion)

    # Do we want to include geographies with low volumes of searches?
    # # Default is yes.
    low_volume = core.string_to_bool(low_volume)

    # ! Pull the trends data for the payload parameters
    geog_df = payload.interest_by_region(resolution=subregion, inc_low_vol=low_volume)

    # Format the new DF to make it easier to read
    # # The region search item is set by default as a pandas DF index. Identify that name.
    region_column = subregion.lower()
    if region_column=='region':
        region_column='state'
    geog_df = gtis_df_formatter(geog_df, ece_topic_code, region_column, rank_sort=True)

    return geog_df


def find_jsons():
    """ Find the JSON files that store dictionary items and return a list of the files.
    0) dma_code_dict.json - Sets a unique identifier (key) for all USA DMA regions (value).
    1) state_dma_dict.json - Connects all DMAs (values) associated with (key) state."""
    cur_path = os.path.realpath(
            os.path.abspath(
                os.path.split(inspect.getfile(inspect.currentframe()))[0]
            )
        )
    dma_id_fil = "dma_code_dict.json"
    state_targ_fil = 'state_dma_dict.json'
    file_names=[dma_id_fil,state_targ_fil]
    json_directory = os.path.join(cur_path, "json")
    if os.path.exists(json_directory) is False:
        potential_json_dir = [root for root, dirs, files in os.walk(cur_path) if dma_id_fil in files][0]
        if os.path.exists(potential_json_dir):
            json_directory =potential_json_dir
            del potential_json_dir
        else:
            print("There was an error finding the JSON dictionary subdirectory.\nFix this issue in a coding bugfix.")
            # Basically, figure out a smart exception later. Just get it working now.
            json_directory = None  # This will error below
    # Set the file paths for the GTrends Json files in a list. Access by indexing downstream.
    list_of_json_dicts = [os.path.join(json_directory, j) for j in file_names if os.path.exists(os.path.join(json_directory, j))]
    return list_of_json_dicts


def json_to_python_dict(json_file):
    """ Pass a json file and return a python dictionary. """
    # ADD TO CCAOA.CORE - will be added for v2.0 release.
    with open(json_file) as open_the_json:
        python_dict = json.load(open_the_json)
    return python_dict


def dma_id_dict():
    """ Returns a dictionary that connects each media market (DMA) to its unique ID. """
    # ID the target ID ~ DMA JSON file
    dma_id_json = find_jsons()[0]
    dma_id_crosswalk= json_to_python_dict(dma_id_json)
    return dma_id_crosswalk


def dmas_all_for_state_dict(state):
    """ For state, extract all associated DMAs & their unique IDs. """
    # Use the appropriate json file.
    state_dma_json = find_jsons()[1]
    # Extract the full contents of the JSON into a python dictionary.
    states_dmas_dict = json_to_python_dict(state_dma_json)
    # return states_dmas_dict  # This would've returned the entire json content. We want just 1 state.
    # Format the state argument correctly.
    state = core.st_upperformat(state)
    # Extract just those DMAs associated with <state>.
    targ_state_dma_dict = states_dmas_dict[state]
    # Return a dict of {ID: DMA,} for <state>
    return targ_state_dma_dict


def related_queries_engine(payload_item, top_not_rising=True):
    """ Extract any Google Trends data you want: any time, any place.
        Note: You MUST provide a payload into this function.
        It is not intended to continuously re-create a payload and will not function that way. """
    if isinstance(payload_item, pytrends.request.TrendReq) is False:
        print("You did not pass a valid payload item into this function. \n"
              "You must create one to use for all you Google Trends extracting needs.\n"
              "Save an item by executing the 'payload_builder()' function and pass it through this one again.")
        return
    rqs_dict=payload_item.related_queries()
    search_item = payload_item.kw_list[0]
    if search_item is None:
        search_item = ece_topic_code
    rqs_dict = rqs_dict[search_item]
    top = rqs_dict['top']
    rising = rqs_dict['rising']

    # Export which item is requested
    if top_not_rising is True:
        if top is not None:
            return top
        else:
            print("There were no 'Top' related keywords for your search item,", search_item)
            return None
    else:
        if rising is not None:
            return rising
        else:
            print("There were no 'Rising' related keywords for your search item,", search_item)
            return None


def top_related_queries(payload_item):
    """ Extract any Google Trends data you want: any time, any place.
        Note: You MUST provide a payload into this function.
        It is not intended to continuously re-create a payload and will not function that way. """
    if isinstance(payload_item, pytrends.request.TrendReq) is False:
        print("You did not pass a valid payload item into this function. \n"
              "You must create one to use for all you Google Trends extracting needs.\n"
              "Save an item by executing the 'payload_builder()' function and pass it through this one again.")
        return
    rq_df = related_queries_engine(payload_item, top_not_rising=True)
    return rq_df


def rising_related_queries(payload_item):
    """ Extract any Google Trends data you want: any time, any place.
        Note: You MUST provide a payload into this function.
        It is not intended to continuously re-create a payload and will not function that way. """
    if isinstance(payload_item, pytrends.request.TrendReq) is False:
        print("You did not pass a valid payload item into this function. \n"
              "You must create one to use for all you Google Trends extracting needs.\n"
              "Save an item by executing the 'payload_builder()' function and pass it through this one again.")
        return
    rq_df = related_queries_engine(payload_item, top_not_rising=False)
    return rq_df


def extract_data(payload_item, spatial_not_temporal=True, region=None, low_volume=True):
    """ Extract any Google Trends data you want: any time, any place.
        Note: You MUST provide a payload into this function.
        It is not intended to continuously re-create a payload and will not function that way. """
    if isinstance(payload_item, pytrends.request.TrendReq) is False:
        print("You did not pass a valid payload item into this function. \n"
              "You must create one to use for all you Google Trends extracting needs.\n"
              "Save an item by executing the 'payload_builder()' function and pass it through this one again.")
        return
    if spatial_not_temporal is True:
        # You have chose to examine spatial data this time with the payload and *not* temportal data.
        # # Run this function again and select "False" for this variable to see temporal trends.

        # Determine which subregion is to be examined.
        region = subregion_identifier(region)
        # Extract data
        extracted_df = extract_spatial_data(payload_item, subregion=region, low_volume=low_volume)

        if region == 'DMA':
            # Add a column to the extract df with the dma's unique ID based on the Schneider DMA shapefile (see README).
            # Extract a dict = {DMA: its_id_number}
            dma_id_reversedict = core.reverse_dict(dma_id_dict())
            # Apply those IDs to the DMAs in the dataframe
            extracted_df["dma_id"] = extracted_df[region.lower()].apply(lambda x: dma_id_reversedict[x])


    else:
        # You have chose to examine spatial data this time with the payload and *not* temportal data.
        # # Run this function again and select "False" for this variable to see temporal trends.

        # Extract data
        extracted_df = extract_temporal_data(payload_item)

    return extracted_df


if __name__ == '__main__':
    from time import time, sleep
    start = time()


    def original_main_testing():
        # Beware of timeout requests:
        # `pytrends.exceptions.ResponseError: The request failed: Google returned a response with code 429.`
        # https://stackoverflow.com/questions/50571317/pytrends-the-request-failed-google-returned-a-response-with-code-429
        the_payload = payload_builder()  # Default args  # Future: pass your timeframe argument into this func.
        sleep(2)  # 2 second pause to trick the Google API?
        states_df = extract_spatial_data(the_payload, subregion='states')
        sleep(2)  # 2 second pause to trick the Google API?
        temporal_df = extract_temporal_data()
        sleep(2)  # 2 second pause to trick the Google API?
        dma_df = extract_spatial_data(the_payload, subregion='DMA')

        print(states_df.head(10))
        print(states_df.tail(10))
        print(temporal_df.head(10))
        print(dma_df.head(10))
        print(dma_df.tail(10))

        # Test adding DMA IDs to the DMA subregion USA DF.
        # Add a column to the extract df with the dma's unique ID based on the Schneider DMA shapefile (see README).
        # Extract a dict = {DMA: its_id_number}
        dma_id_reversedict = core.reverse_dict(dma_id_dict())
        # Apply those IDs to the DMAs in the dataframe
        dma_df["dma_id"] = dma_df["DMA".lower()].apply(lambda x: dma_id_reversedict[x])
        print(dma_df.head(10))

    # Beware of timeout requests:
    # `pytrends.exceptions.ResponseError: The request failed: Google returned a response with code 429.`
    # https://stackoverflow.com/questions/50571317/pytrends-the-request-failed-google-returned-a-response-with-code-429
    usa_payload = payload_builder()  # Default args  # Future: pass your timeframe argument into this func.
    # Reformat the below with extract_data(payload_item, spatial_not_temporal=True, region=None, low_volume=True) func.
    sleep(2)  # 2 second pause to trick the Google API?
    usa_states_df = extract_data(usa_payload, region='states', spatial_not_temporal=True)
    sleep(2)  # 2 second pause to trick the Google API?
    usa_temporal_df = extract_data(usa_payload, spatial_not_temporal=False)
    sleep(2)  # 2 second pause to trick the Google API?
    usa_dma_df = extract_data(usa_payload, spatial_not_temporal=True,region='DMA')

    print(usa_states_df.head(10))
    print(usa_states_df.tail(10))
    print(usa_temporal_df.head(10))
    print(usa_dma_df.head(10))
    print(usa_dma_df.tail(10))

    # # Test a state-specific trend pull
    # maryland_payload = payload_builder(geography_broad='US-MD')
    # ky_payload = payload_builder(geography_broad='US-KY')

    core.runtime(start)
