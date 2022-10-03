import inspect


def retrieve_singlevar_name(var):
    """ Courtesy of https://stackoverflow.com/a/18425523/15517267 """
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var][0]


def store_data(storage_directory_file_path,gtrends_data):
    """ Store the GTrends data you just pulled. """
    # Get the name of the variable for downstream storage naming metadata.
    dataset_name = retrieve_singlevar_name(gtrends_data)

    return


