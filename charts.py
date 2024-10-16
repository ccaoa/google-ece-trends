import os, time, numpy as np, pandas as pd
import glob, matplotlib.pyplot as plt, seaborn as sns

from ccaoa import core, raccoon as rc

try:
    from . import dma, store_data as store, trend_calculations as tcalc, append as app
except ImportError:
    import dma, store_data as store, trend_calculations as tcalc, append as app


sum_data_pth = app.summary_storage_path()


def geog_rsv_histogram(dma_only: bool = True, national_only: bool = False):
    """ Get histograms that show the frequency of relative search volumes (RSVs) across different geographic datasets"""

    # Search for Excel files with '_summary_' in the filename but not '_qs_'
    excel_files = glob.glob(os.path.join(sum_data_pth, '*_summary_*.xlsx'))
    excel_files = [f for f in excel_files if '_qs_' not in f and "_time_" not in f]
    if dma_only:
        # No state level results
        excel_files = [f for f in excel_files if "_dma_" in f]
    # else:
    #     excel_files = [f for f in excel_files if "_states_" in f]
    if national_only:
        # Nation-level results
        excel_files = [f for f in excel_files if ('valentines_' in f or 'usa_' in f)]
    else:
        excel_files = [f for f in excel_files if ('valentines_' not in f and 'usa_' not in f)]

    # Initialize a list to store the data from all files
    rebse_data = []

    # Iterate over each file to read the 'rebse_gtis' column
    for file in excel_files:
        df = pd.read_excel(file)
        if 'rebse_gtis' in df.columns:
            rebse_data.extend(df['rebse_gtis'].dropna().tolist())

    # Create a plot to visualize the distribution of 'rebse_gtis' across all files
    plt.figure(figsize=(10, 6))
    sns.histplot(rebse_data, bins=20, kde=True, color='skyblue')

    # Set plot labels and title
    plt.xlabel('Rebse GTIS Value (0-100)')
    plt.ylabel('Frequency')
    plt.title('Distribution of Rebased RSV Values Across Only DMA National Summary Files')
    plt.xlim(0, 100)

    # Show the plot
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    geog_rsv_histogram(dma_only=True,national_only=False)
