import re
import numpy as np
import scipy.stats as stats
sum_file_paths = [
'ky_time_20180603-20220910.xlsx',
'tx_time_20210321-20210421.xlsx',
'usa_dma_df_20180603-20220910.xlsx',
'eugene_time_20200214-20210214.xlsx',
'ky_dma_20180603-20220910.xlsx'
]
sheet = "raw_data_records"
results = []
for file in sum_file_paths:
    df = pd.read_excel(file, sheet_name=sheet)
    for column in df.columns:
        if column != 'pull_date':
            non_null_values = df[column].dropna()
            # Measure of central tendency: Mean
            mean = non_null_values.mean()
            # Measure of central tendency: Median for comparison.
            median = non_null_values.median()
            # Measure of uncertainty: Standard Error at 95% confidence interval
            ci = stats.norm.interval(0.95, loc=mean, scale=stats.sem(non_null_values))
            # Number of non-null observations
            non_null_count = non_null_values.count()
            results.append([file, column, mean, median, ci, non_null_count])
results_df = pd.DataFrame(results, columns=['File', 'Subject', 'Mean', 'Median', 'Confidence Interval', 'Non-null Count'])
print(results_df.tail(11))
