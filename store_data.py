import inspect, datetime as dt, os

from ccaoa import core


def retrieve_singlevar_name(var):
    """ Courtesy of https://stackoverflow.com/a/18425523/15517267 """
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var][0]


def date_from_searchperiod(search_period_date):
    """ Use DateTime to extract the date of the search period. """
    # EX: '2020-02-14 2021-02-14'
    firstdate = search_period_date[:10].replace('-','')
    seconddate = search_period_date[11:21].replace('-','')
    date_range = firstdate + '-' + seconddate

    return date_range


def store_data(storage_directory_file_path,gtrends_data, search_date_period, gtrends_file_name=None,csv_not_xlsx=True):
    """ Store the GTrends data you just pulled. """
    # Get the name of the variable for downstream storage naming metadata.
    if gtrends_file_name is None:
        dataset_name = retrieve_singlevar_name(gtrends_data)
    else:
        dataset_name =gtrends_file_name
    date_range = date_from_searchperiod(search_date_period)
    today = dt.datetime.today().strftime('%Y%m%d')

    if csv_not_xlsx is True:
        ext = ".csv"
    else:
        ext = '.xlsx'

    file_name = dataset_name + "_" + date_range +"_"+today+ext
    file_path = os.path.join(storage_directory_file_path,file_name)
    core.df_to_file(gtrends_data,file_path)

    return


