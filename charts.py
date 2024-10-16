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


def plot_temporal_rsv():
    """ Plot temporal RSV data with confidence intervals for each temporal dataset."""

    # Search for Excel files with 'temporal' or 'time' in the filename
    excel_files = glob.glob(os.path.join(sum_data_pth, '*temporal*.xlsx')) + glob.glob(os.path.join(sum_data_pth, '*time*.xlsx'))
    excel_files = [f for f in excel_files if '_qs_' not in f and "_raw_data_records" not in f]
    # Iterate over each file to read and plot 'gtis_mean' data
    plt.figure(figsize=(12, 8))
    et = "event_time"
    for file in excel_files:
        label = os.path.basename(file).split('.')[0].replace("_temporal_", "_").replace("_df_", "_").replace(
            "_summary_stats", '').replace('valentines', 'usa').replace('_', " ").upper()
        df = pd.read_excel(file)
        if 'gtis_mean' in df.columns and et in df.columns:
            # Extract columns for plotting
            df[et] = pd.to_datetime(df[et], errors='coerce')
            df = df.sort_values(by=et)
            event_time = df[et]
            gtis_mean = df['gtis_mean']
            ci_lower = df['ci_95_lowr'] if 'ci_95_lowr' in df.columns else df['ci_95_pct'].apply(lambda x: x[0] if pd.notna(x) else None)
            ci_upper = df['ci_95_uppr'] if 'ci_95_uppr' in df.columns else df['ci_95_pct'].apply(lambda x: x[1] if pd.notna(x) else None)

            # Plot the mean values as a line
            plt.plot(event_time, gtis_mean, color="black", label="Mean RSV")

            # Plot the confidence interval as a shaded area
            plt.fill_between(event_time, ci_lower, ci_upper, alpha=0.6, color="gray",label='95% Confidence Interval')
        else:
            print(label, 'not valid.')

        # Set plot labels and title
        plt.xlabel('Search Period')
        plt.ylabel('Average Relative Search Volume')
        plt.title('Temporal RSV Data: '+label)

        # plt.suptitle(label)
        plt.legend()

        # Show the plot
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    # geog_rsv_histogram(dma_only=True,national_only=False)
    plot_temporal_rsv()
