import os

try:
    from . import pull_data as pull, store_data as store, dma, summarize as agg
except ImportError:
    import pull_data as pull, store_data as store, dma, summarize as agg


def append_everything(raw_dir_path):
    all_fils_basenames = os.listdir(raw_dir_path)
    targ_files_listdir = [os.path.join(raw_dir_path, af) for af in all_fils_basenames]
    # Append all the raw target files to the summary sheets.
    # # If a summary sheet is not yet set up, it should be created.
    # [agg.append_raw_data_fromfile(tf) for tf in targ_files_listdir]
    # Use for loop to do some helpful print statements
    print("Appending raw files.")
    counter = 0
    allfils = len(targ_files_listdir)
    for tf in targ_files_listdir:
        agg.append_raw_data_fromfile(tf)
        counter+=1
        print(counter,'/',allfils,"processed:   ",os.path.basename(tf))
    print("---------------------------------------------------------------")


def summarize_collected_data(list_of_summary_datasets: list):
    """
    Use a list of summary xlsx datasets representing distinct and unique G Trends instances for which you're collecting
    samples and summarize all the raw data records already recorded in the summary sheets
    """
    # [agg.calc_sumstats(sd) for sd in list_of_summary_datasets]
    # Use for loop to do some helpful print statements
    print("Summarizing files.")
    counter = 0
    allfils = len(list_of_summary_datasets)
    for sd in list_of_summary_datasets:
        agg.append_raw_data_fromfile(sd)
        counter+=1
        print(counter,'/',allfils,"processed:   ",os.path.basename(sd))
    print("---------------------------------------------------------------")


base_path = os.path.expanduser(r"~\NACCRRA\Research Team - Documents\Mapping\google_trends\gtrends_data")
raw_data = os.path.join(base_path,"raw_data")
sum_data = os.path.join(base_path,"summary_data")
unique_twentythree_rawdatasets = [tt for tt in os.listdir(raw_data) if tt[len(tt)-len('20230104.csv'):]=='20230104.csv']
# Append all raw data to their designated summary XLSXs
append_everything(raw_data)
# Now list the full directory of summary data.
targ_sumfiles_listdir = [os.path.join(sum_data, sdx) for sdx in os.listdir(sum_data)]
summarize_collected_data(targ_sumfiles_listdir)
