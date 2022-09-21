import pandas as pd
from ccaoa import core
from pytrends.request import TrendReq


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



def payload_builder(timeframe=None, search_item="%2Fm%2F022hpx",geography_broad='US', connection_item=None):
    """ The payload is the base parameter set that tells Google the broad picture of what you're trying to research:
    the 'What, Where, & When' of GTrends data pulls. 
    The 'When' is likely to be the most variable for CCAoA. Formatting this argument will likely take its own function. 
    What = the child care topic.
    Where = USA (while state specific searches could be used, you run the risk of the Cincinnati Problem). """

    # TIMEFRAME
    # Set a placeholder timeframe for now
    if timeframe is None:
        timeframe = '2020-02-14 2021-02-14'

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
