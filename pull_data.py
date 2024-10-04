"""
Script providing functions for easy and custom pulls of Google Trends data for different times and places.
Heavily inspired by:
* https://github.com/GeneralMills/pytrends
* https://github.com/Tanu-N-Prabhu/Python/blob/master/Google_Trends_API.ipynb
"""

import pandas as pd
from ccaoa import core
import pytrends
from pytrends.request import TrendReq

try:
    from . import dma
except:
    import dma

ece_topic_code = "%2Fm%2F022hpx".replace("%2F", r"/")
worker_topic_code = "%2Fg%2F11bc6xhvhf".replace("%2F", r"/")
prek_topic_code = "%2Fm%2F027wyv".replace("%2F", r"/")


def backoff_factor_calculator(retries=2, backoff_factor=0.1):
    """Calculator to figure out how many seconds would elapse using a particular number of retries by the submitted backoff factor.
    See https://github.com/GeneralMills/pytrends#connect-to-google for more."""
    loops = 0
    raw_sleeps = []
    while loops < retries:
        sleep_seconds = backoff_factor * (2 ** ((loops + 1) - 1))
        raw_sleeps.append(sleep_seconds)
        loops += 1
    # Convert the raw seconds to readable text
    prt_sleeps = []
    for slp in raw_sleeps:
        if slp >= 60:
            minutes = int(slp / 60)
            minutes_remainder = slp % 60
            seconds = int(minutes_remainder)
            add_text = str(minutes) + " min, " + str(seconds) + " sec"
        else:
            add_text = str(slp) + " sec"
        prt_sleeps.append(add_text)

    return prt_sleeps


def connect_to_gtrends(language="en-US", retries=10, backoff_factor=0.1):
    """This is a shell function for pytrends.request.TrendReq().
    That function takes several arguments, but until they are better understood, the defaults will be used.
    """

    # LANGUAGE
    # Likely will need to flesh out this argument to dynamically select more than US English, but start with that.
    if "english" in language.lower():
        language = "en-US"

    # Connect to Google Trends; open the gateway.
    ptrend = TrendReq(
        hl="en-US",
        # tz=360,
        tz=abs(
            300
        ),  # Eastern Standard Time  # https://forbrains.co.uk/international_tools/earth_timezones
        # timeout=(10,25),
        # retries=2, backoff_factor=0.1,
        retries=retries,
        backoff_factor=backoff_factor,
        # requests_args={'verify':False} #,proxies=['https://34.203.233.13:80']}#
    )
    return ptrend


def payload_builder(
    timeframe: str = None,
    geography_broad: str = "US",
    search_item: str = None,
    connection_item=None,
):
    """The payload is the base parameter set that tells Google the broad picture of what you're trying to research:
    the 'What, Where, & When' of GTrends data pulls.
    The 'When' is likely to be the most variable for CCAoA. Formatting this argument will likely take its own function.
    What = the child care topic.
    Where = USA (while state specific searches could be used, you run the risk of the Cincinnati Problem).
    """

    # TIMEFRAME
    # https://github.com/GeneralMills/pytrends#interest-by-region:~:text=is%20%27360%27-,timeframe,-Date%20to%20start
    # Fully Formatting this argument will likely take creating its own function.
    # # Defaults to last 5yrs, 'today 5-y'
    # # Note Time component is based off UTC
    # Set a placeholder timeframe for now
    if timeframe is None:
        timeframe = "2020-02-14 2021-02-14"  # The COVID Valentines' study period.

    # SEARCH TERM, TOPIC, OR CATEGORY
    # Assume the prominently consistent search item is the topic of Child Care, "%2Fm%2F022hpx"
    # Don't use child care category. Returns insignificant results in browser, so maybe unreliable pytrends data.
    # # 403 is the Child Care category, but that's not returning much.
    # Instead, search for the Child care "Topic", what has been used for initial research.
    # You can search for topics by following this methodology: https://github.com/GeneralMills/pytrends/issues/437
    # It must be translated to (see issue link above):
    if not search_item:
        search_item = ece_topic_code
    search_item = search_item.replace("%2F", r"/")

    # GEOGRAPHY
    # Set up framework here for if a user passes a state to transform it into the correct format for the payload build.
    usa_list = ["USA", "US", "UNITEDSTATES", "AMERICA"]
    geography_broad = str(geography_broad)
    if geography_broad.replace(" ", "").upper() not in usa_list:
        statesearch = core.st_upperformat(
            geography_broad.replace("US-", ""), suppress_print=True
        )
        if statesearch in core.statedict():
            # The first two characters (excluding 'US-') are a state. Means we have a valid state or DMA geog.
            if statesearch == "DC":
                # DC is not considered an admin 1 by GTrends but an Admin 2 (DMA).
                geography_broad = "US-MD-511"
            # Else, if two dashes in the geography and the last 3 characters are a valid DMA ID:
            elif (
                str(geography_broad).count("-") == 2
                and str(
                    geography_broad[len(geography_broad) - 3 : len(geography_broad)]
                )
                in dma.dma_id_to_name_dict()  # dma_id_dict()
            ):
                # A geography with
                #   1) a valid state state in the correct position,
                #   2) 2 dashes, &
                #   3) the last 3 characters are a valid DMA ID
                # likely indicates a DMA is being passed as the broad geography.
                # print('Running with the DMA', geography_broad)
                pass  # essentially, geography_broad = geography_broad
            else:
                geography_broad = "US-" + statesearch
        # Eventually add options to drill into DMAs themselves. Use the state_dma_dict.
        else:
            # Default to the entire USA
            geography_broad = "US"
    else:
        # Default to the entire USA
        geography_broad = "US"

    # Build the payload
    if connection_item is None:
        # Connect to Google using my default arguments.
        connection_item = connect_to_gtrends()
    connection_item.build_payload(
        kw_list=[search_item], timeframe=timeframe, geo=geography_broad
    )

    return connection_item


# Now, from a built payload, you can extract all sorts of stuff by accessing properties of the payload variable.
#     # Probably the most popular will be spatial and temporal.
#     # payload.interest_over_time()  # Temporal
#     # payload.interest_by_region()  # Spatial
#     # payload.related_topics()
#     # payload.related_queries()
#     # payload.get_historical_interest(keywords)


def index_as_first_col(indf, new_col_name):
    """Set the index of a pandas data frame as its first column with a new arbitrary index."""
    outdf = indf.copy()
    outdf[new_col_name] = outdf.index
    # Set new col name for the former IDX as first column
    cols = outdf.columns.to_list()
    cols = cols[-1:] + cols[:-1]
    outdf = outdf[cols]
    # Reset the index to be numerical.
    outdf = outdf.reset_index(drop=True)
    return outdf


def gtis_df_formatter(payload_df, search_term, uoa, rank_sort=True):
    """Generates a clean DF with a formatted GTIS column for either time or geography results
    with an optional ranking column for each UOA region."""

    # Rename the Google Trends Interest Score (GTIS) column
    score_column_name = "gtis"
    payload_df = payload_df.rename(columns={search_term: score_column_name})
    # The date/geography variable item is set by default as a pandas DF index. We want it as an actual, physical column.
    # # If temporal, UOA should be = 'date'
    # # # (See if this differs as time period for results differs. I.e. if UOA is a week vs a day).
    # # # # If it does, see spatial function way of resolving multiple possible UOAs.
    # # If spatial, UOA will vary: uoa_resolutions =['COUNTRY','REGION','DMA','CITY']
    # payload_df[uoa] = payload_df.index
    # # Set UOA col as first column
    # cols = payload_df.columns.to_list()
    # cols = cols[-1:] + cols[:-1]
    # payload_df = payload_df[cols]
    # # Reset the index to be numerical.
    # payload_df = payload_df.reset_index(drop=True)
    payload_df = index_as_first_col(payload_df, uoa)

    # Add a rank to the dataframe. Only sort if geography.
    # if rank is True:
    rank_dataframe = pd.DataFrame(list(range(1, len(payload_df) + 1)), columns=["rank"])
    # Include the rankings in the payload dictionary
    if rank_sort is True:
        payload_df = pd.concat(
            # Sorted version of the GTrends Data
            [
                payload_df.sort_values(score_column_name, ascending=False).reset_index(
                    drop=True
                ),
                # Merge regional data with its GTIS ranking
                rank_dataframe,
            ],  # .astype(int)]  # Strangely, setting astype to int gives it a decimal...
            axis=1,
        )
    else:
        # Rank results without sorting.
        dfforrank = pd.concat(
            # Sorted version of the GTrends Data
            # # Don't reset the index. Generates its own 'index' column to reference later.
            [
                payload_df.sort_values(score_column_name, ascending=False).reset_index(
                    False
                ),
                # Merge regional data with its GTIS ranking
                rank_dataframe,
            ],  # .astype(int)]
            axis=1,
        )
        # Get your DF in it's OG order again.
        dfforrank = dfforrank.sort_values("index", ascending=True)
        # payload_df = dfforrank.drop('index')
        payload_df = dfforrank.set_index("index")
        del dfforrank

    del rank_dataframe

    # Set the UOA column as the first in the df
    payload_df = payload_df[[uoa] + [col for col in payload_df.columns if col != uoa]]

    return payload_df


def extract_temporal_data(
    payload=None, time_uoa: str = "date", topic_code: str = None
) -> pd.DataFrame:
    """Pass a connection item with a built payload into this function to extract meaningful time data from it."""

    if not payload:
        # Thinking defining the timeframe outside of this function will be wise. Too much nesting otherwise.
        payload = payload_builder()
    if not topic_code:
        topic_code = ece_topic_code

    # Pull the time data for the payload parameters
    time_df = payload.interest_over_time()

    # Format the new DF to make it easier to read
    time_df = gtis_df_formatter(time_df, topic_code, time_uoa, rank_sort=False)

    return time_df


def subregion_identifier(subregion_input):
    """Figure out what sub-region of your payload's broader geography you want to explore."""

    # The default is "REGION", the international code for subnational UOAs (Admin Level 1).
    # # For the US, this is States.
    # However, useful also in the US are media markets, specifically Nielsen Designated Market Areas (DMAs).
    # # This is the last continuous geography in the USA.
    # 'COUNTRY' returns country level data. In case you wanted one score for the whole US?
    # # This is the broadest, least precise geographic UOA supported.
    #
    # Finally, there are cities. 'CITY' returns city level data.
    # # However, be warned: pytrends v4.8 in PyPi does not support all runs of City UOA trends.
    # # # That version was updated 1 Feb 2022.
    # # # https://pypi.org/project/pytrends/
    # # Running with "CITY" as UOA of subregion results in:
    # # # * states for country payloads
    # # # * DMAs for state payloads
    # # # * errors for DMA payloads
    # # This is a known issue logged in GitHub:
    # # # Issue https://github.com/GeneralMills/pytrends/issues/392
    # # # Merged to Master by pull request https://github.com/GeneralMills/pytrends/pull/509 in GitHub on 26 Mar 2022.
    # # # Issue https://github.com/GeneralMills/pytrends/issues/316 still remains open; TBD if PR #509 fixes.
    # # # Unclear if issue 497 is applicable; pertains to non-USA regions, but user experiencing similar issue as above.
    # # # # https://github.com/GeneralMills/pytrends/issues/497
    # # But, Pull Request 509 has not been applied to the PyPi version of the repo.
    # # So, as long as PyPi remains behind GitHub, `pip install pytrends` will not be sufficient to work with cities.
    # # Solutions: pip install directly from GitHub or wait for new pytrends release.
    # # Also see: https://stackoverflow.com/questions/61435486/pytrends-fail-to-get-us-city-level-data
    # # UPDATE: As of January 2023, the desired updates above *should* be included in v4.9.0.
    # # # https://pypi.org/project/pytrends/4.9.0/
    # # # While v4.8 in PyPi did not have Pull Request 509 included and GitHub's did, both v4.9 should include this.
    # # # Upgrade to ~=4.9 to inherit.
    # # # https://github.com/GeneralMills/pytrends/releases/tag/v4.9.0
    uoa_resolutions = ["COUNTRY", "REGION", "DMA", "CITY"]

    if subregion_input is None:
        subregion = subregion_input
    elif subregion_input.upper().replace(" ", "") not in uoa_resolutions:
        if subregion_input.lower().replace(" ", "") in ["state", "states", "usstates"]:
            subregion = "REGION"
        elif subregion_input.lower().replace(" ", "") in ["county", "counties"]:
            print(
                "Counties are not tracked by Google Trends. "
                "The closest you can get for sub-state data is media markets.\n"
                "Returning data for media markets."
            )
            subregion = "DMA"
        else:
            print(
                "Your entered geography value",
                subregion_input,
                "was not valid; defaulting to State analysis.",
            )
            subregion = "REGION"
    else:
        subregion = subregion_input

    return subregion


def extract_spatial_data(
    payload=None, subregion="REGION", low_volume=True, topic_code: str = None
) -> pd.DataFrame:
    """Pass a connection item with a built payload into this function to extract meaningful geography data from it.
    This will look at Trends across Sub-Geographies as Units of Analysis (UOAs)"""

    if not payload:
        payload = payload_builder()
    if not topic_code:
        topic_code = ece_topic_code

    # Determine which subregion is to be examined.
    subregion = subregion_identifier(subregion)

    # Do we want to include geographies with low volumes of searches?
    # # Default is yes.
    low_volume = core.string_to_bool(low_volume)

    # ! Pull the trends data for the payload parameters
    geog_df = payload.interest_by_region(resolution=subregion, inc_low_vol=low_volume)

    # Format the new DF to make it easier to read
    # # The region search item is set by default as a pandas DF index. Identify that name.
    if subregion is None:
        region_column = None
    else:
        region_column = subregion.lower()
    if region_column == "region":
        region_column = "state"
    geog_df = gtis_df_formatter(geog_df, topic_code, region_column, rank_sort=True)

    return geog_df


def related_queries_engine(payload_item, top_not_rising=True):
    """Extract any Google Trends data you want: any time, any place.
    Note: You MUST provide a payload into this function.
    It is not intended to continuously re-create a payload and will not function that way.
    """
    if isinstance(payload_item, pytrends.request.TrendReq) is False:
        print(
            "You did not pass a valid payload item into this function. \n"
            "You must create one to use for all you Google Trends extracting needs.\n"
            "Save an item by executing the 'payload_builder()' function and pass it through this one again."
        )
        return
    rqs_dict = payload_item.related_queries()
    search_item = payload_item.kw_list[0]
    if not search_item:
        search_item = ece_topic_code
    rqs_dict = rqs_dict[search_item]
    top = rqs_dict["top"]
    rising = rqs_dict["rising"]

    # Export which item is requested
    if top_not_rising is True:
        if top is not None:
            return top
        else:
            print(
                "There were no 'Top' related keywords for your search item,",
                search_item,
            )
            return None
    else:
        if rising is not None:
            return rising
        else:
            print(
                "There were no 'Rising' related keywords for your search item,",
                search_item,
            )
            return None


def top_related_queries(payload_item):
    """Extract any Google Trends data you want: any time, any place.
    Note: You MUST provide a payload into this function.
    It is not intended to continuously re-create a payload and will not function that way.
    """
    if isinstance(payload_item, pytrends.request.TrendReq) is False:
        print(
            "You did not pass a valid payload item into this function. \n"
            "You must create one to use for all you Google Trends extracting needs.\n"
            "Save an item by executing the 'payload_builder()' function and pass it through this one again."
        )
        return
    rq_df = related_queries_engine(payload_item, top_not_rising=True)
    return rq_df


def rising_related_queries(payload_item):
    """Extract any Google Trends data you want: any time, any place.
    Note: You MUST provide a payload into this function.
    It is not intended to continuously re-create a payload and will not function that way.
    """
    if isinstance(payload_item, pytrends.request.TrendReq) is False:
        print(
            "You did not pass a valid payload item into this function. \n"
            "You must create one to use for all you Google Trends extracting needs.\n"
            "Save an item by executing the 'payload_builder()' function and pass it through this one again."
        )
        return
    rq_df = related_queries_engine(payload_item, top_not_rising=False)
    return rq_df


def extract_data(
    payload_item,
    spatial_not_temporal=True,
    region=None,
    low_volume=True,
    suppress_prints=True,
):
    """Extract any Google Trends data you want: any time, any place.
    Note: You MUST provide a payload into this function.
    This function is not intended to continuously re-create a payload and will not function that way.
    This is to prevent Google 429 errors."""
    if isinstance(payload_item, pytrends.request.TrendReq) is False:
        print(
            "You did not pass a valid payload item into this function. \n"
            "You must create one to use for all you Google Trends extracting needs.\n"
            "Save an item by executing the 'payload_builder()' function and pass it through this one again."
        )
        return
    if spatial_not_temporal is True:
        # You have chose to examine spatial data this time with the payload and *not* temportal data.
        # # Run this function again and select "False" for this variable to see temporal trends.

        # Determine which subregion is to be examined.
        region = subregion_identifier(region)
        # Extract data
        extracted_df = extract_spatial_data(
            payload_item, subregion=region, low_volume=low_volume
        )

        if region == "DMA":
            # Add a column to the extract df with the dma's unique ID based on the Schneider DMA shapefile (see README).
            # Apply the IDs to the DMAs in the dataframe in a new column
            # # Note: This could become a function within the dma.py to inherit in the future.
            # # # Multiple downstream files need this DataFrame application of a DMA ID, so function-ize it.
            extracted_df["dma_id"] = extracted_df[region.lower()].apply(
                lambda x: dma.dma_id_name_converter(x)
            )

        if suppress_prints is False:
            print(
                payload_item.geo,
                "Google Trends data for",
                region.lower().replace("region", "state") + "s",
                "complete.",
            )

    else:
        # You have chose to examine spatial data this time with the payload and *not* temportal data.
        # # Run this function again and select "False" for this variable to see temporal trends.

        # Extract data
        extracted_df = extract_temporal_data(payload_item)

        if suppress_prints is False:
            print(
                payload_item.geo,
                "Google Trends data for time range",
                str(payload_item.interest_over_time_widget["request"]["time"]),
                "complete.",
            )

    return extracted_df


def extract_data_try(
    payload_item,
    spatial_not_temporal=True,
    region=None,
    low_volume=True,
    suppress_prints=True,
):
    """
    Try using the `extract_data()` function to dynamically pull Google Trends Data.
    In the event of a Google 429 error, return None instead of erroring and killing the entire script run.
    This will allow downstream manipulation of code to run and rerun data extractions regardless of Google blockades.
    """
    try:
        ret_item = extract_data(
            payload_item=payload_item,
            spatial_not_temporal=spatial_not_temporal,
            region=region,
            low_volume=low_volume,
            suppress_prints=suppress_prints,
        )
    except Exception as ex:
        if spatial_not_temporal is True:
            prt = (
                str(payload_item.geo)
                + "'s "
                + region.lower().replace("region", "state")
                + " regions"
            )
        else:
            # Need to extract the broad geography from the payload item.
            prt = (
                "temporal trends for "
                + str(payload_item.geo)
                + " for timeframe "
                + str(payload_item.interest_over_time_widget["request"]["time"])
            )
        print(
            "Extraction pull for",
            prt,
            "was unsuccessful. Returning `None` item. Error:\n   ",
            str(ex),
        )
        ret_item = None

    return ret_item


if __name__ == "__main__":
    from time import time, sleep

    start = time()

    def original_main_testing():
        # Beware of timeout requests:
        # `pytrends.exceptions.ResponseError: The request failed: Google returned a response with code 429.`
        # https://stackoverflow.com/questions/50571317/pytrends-the-request-failed-google-returned-a-response-with-code-429
        # This should be fixed with the new backoff_factor elements of the payload builder.
        init_late2022_studyperiod = "2018-06-03 2022-09-10"
        the_payload = payload_builder(
            timeframe=init_late2022_studyperiod
        )  # Default args
        # sleep(2)  # 2 second pause to trick the Google API?  # No longer necessary with the backoff_factor applied.
        states_df = extract_data_try(
            # extract_spatial_data(the_payload, subregion="states")
            the_payload,
            spatial_not_temporal=True,
            region="states",
            low_volume=True,
            suppress_prints=False,
        )
        temporal_df = extract_temporal_data()
        # Below equates to extract_spatial_data(the_payload, subregion='DMA')
        dma_df = extract_data_try(the_payload, spatial_not_temporal=True, region="DMA")

        print(states_df.head(10))
        print(states_df.tail(10))
        print(temporal_df.head(10))
        print(temporal_df.tail(10))
        print(dma_df.head(10))
        print(dma_df.tail(10))

    # original_main_testing()

    core.runtime(start)
