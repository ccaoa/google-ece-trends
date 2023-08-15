import os

try:
    from . import pull_data as pull, store_data as store, dma, summarize as agg
except ImportError:
    import pull_data as pull, store_data as store, dma, summarize as agg


base_path = os.path.expanduser(r"~\NACCRRA\Research Team - Documents\Mapping\google_trends\gtrends_data")
raw_data = store.get_storage_path()
sum_data = os.path.join(base_path,"summary_data")
unique_twentythree_rawdatasets = [tt for tt in os.listdir(raw_data) if tt[len(tt)-len('20230104.csv'):]=='20230104.csv']
# all_fils_basenames = os.listdir(raw_dir_path)
# targ_files_listdir = [os.path.join(raw_dir_path, af) for af in all_fils_basenames]
# Append all raw data to their designated summary XLSXs
agg.append_all_raw_files(raw_data)
# Now list the full directory of summary data.
# targ_sumfiles_listdir = [os.path.join(sum_data, sdx) for sdx in os.listdir(sum_data)]
agg.summarize_all_summary_data(sum_data)
