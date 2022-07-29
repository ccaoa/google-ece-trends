# Venv testing
# import pytrends
# from ccaoa import quick
# print("Successful pytrends import. Huzzah!")

# Methodology testing
# # adpted from https://github.com/Tanu-N-Prabhu/Python/blob/master/Google_Trends_API.ipynb
import pandas as pd
from pytrends.request import TrendReq
ptrend = TrendReq(
    # hl='en-US', tz=360, timeout=(10,25), proxies=['https://34.203.233.13:80',], retries=2, backoff_factor=0.1, requests_args={'verify':False}
)

# Get Google Hot Trends data
hottrenddf = ptrend.trending_searches(pn='united_states')
hottrenddf.head()

# PAYLOAD TESTING

# # Build an initial payload for the search term of Child Care.
# primary_search_term = 'Child care'
# ptrend.build_payload(
#     # Keywords to search for
#     # # Can this list be blank?  # initial tests indicate no; must be filled with keyword.
#     kw_list=[primary_search_term],#[],#
#     # # Search Category; Defaults to no category
#     # # # Child Care is category #403 according to https://github.com/pat310/google-trends-api/wiki/Google-Trends-Categories
#     # # Initial test returned no results with this argument included as either string or integer
#     # cat='403',
#     # See time parameters https://github.com/GeneralMills/pytrends#:~:text=is%20%27360%27-,timeframe,-Date%20to%20start
#     timeframe='2019-01-01 2021-12-31',  # default: 'today 5-y',
#     # Geography; # Defaults to World;
#     # # More detail available for States/Provinces by specifying additional abbreviations.
#     # # # For example: Alabama would be 'US-AL'; For example United States is 'US'
#     geo='US',
#     # # Google Property to search
#     # # # Defaults to web searches, but it can also be images, news, youtube or froogle (for Google Shopping results)
#     # gprop='',
# )
#
# # Try a category payload
# # See if we can get a category from the API
# words_key = ptrend.suggestions(keyword=primary_search_term)
# keywords_df = pd.DataFrame(words_key).drop(columns='mid')
# # First record is the Child care topic

# # Try getting topical results by following the advice in this issue.
# # # https://github.com/GeneralMills/pytrends/issues/451
# ptrend.build_payload(
#     # # Can this list be blank?  # initial tests indicate no; must be filled with keyword.
#     kw_list=[''],#primary_search_term],#[],#
#     cat='403',
#     timeframe='2019-01-01 2021-12-31',
#     geo='US'
# )
# Don't use child care category. Returns insignificant results in browser, so maybe unreliable pytrends data.

# So actually, the "Category" is not the real specific that we want.
# 403 is the Child Care category, but that's not returning much.
# Instead, search for the Child care "Topic", what I've been searching with all along.
# You can search for topics by following this methodology: https://github.com/GeneralMills/pytrends/issues/437
# Looks like the topic code for Child care is:
topic_chrome_code = "%2Fm%2F022hpx"
# Which must be translated to (see issue link above):
topic_code_translation = topic_chrome_code.replace("%2F",r"/")
# So, go try it out!
# # For the full build_payload() variable notes, see above with the original search term comments
ptrend.build_payload(
    # Fill the keyword list with the formatted child care topic.
    kw_list=[topic_code_translation],
    # cat='403', # Don't use this data. Returns insignificant results in browser, so maybe unreliable pytrends data.
    timeframe='2020-02-14 2021-02-14',  # My classic COIVD timeperiod
    geo='US'
)
# Success!

# NOW THAT THE PAYLOAD IS BUILT, EXPLORE THE DATA YOU HAVE COLLECTED.

# Geography
score_column_name = topic_code_translation # primary_search_term
region_df = ptrend.interest_by_region(resolution='REGION')#resolution='DMA', inc_low_vol=True, inc_geo_code=False)
region_df.head(9)  # alphabetical
# # Rename the score column
# region_df.columns=region_df.columns.str.replace("/","_")#.replace("/","_")
region_df=region_df.rename(columns={score_column_name: "gtis"})#, inplace=True)
score_column_name = 'gtis'
# See the leading 10 entries
region_df.sort_values(score_column_name, ascending=False).head(9)
# # Testing notes
# * The order of the items is the same as manually going to google trends online.
#   However, the values are *slightly* off. By only 1 usually.
# * The original example above does indeed return a child care search term, not a topic.

# Add the state index as a column to the df
region_df["state"] = region_df.index
# Set state col as first column
colsreg = region_df.columns.to_list()
colsreg = colsreg[-1:] + colsreg[:-1]
region_df=region_df[colsreg]
# Reset the index to be numerical.
region_df = region_df.reset_index(drop=True)#, inplace=False)

# Print the dataframe with a rank
rank_df = pd.DataFrame(list(range(1,52)),columns=["rank"])
pd.concat(
    # Sorted version of the GTrends Data
    [region_df.sort_values(score_column_name, ascending=False).reset_index(drop=True),
     # Merged with a ranking
     rank_df.astype(int)]
    ,axis=1
).head(10)


# TEMPORAL TRENDS
# Try a basic time command
overtime_df = ptrend.interest_over_time()
# Gives you weekly time data
overtime_df=overtime_df.rename(columns={topic_code_translation: "gtis"})
