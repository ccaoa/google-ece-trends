import os, sys, numpy as np, pandas as pd, math


def rebase_math(gtisr_singlescore, max_gtisr_val=55.13899994):
    """This function will normalize the county-level Google Trends Interest Score (GTIS) or Ratio (GTIR)
    by taking the maximum score of the sample and setting it = to 100.
    All other scores are proportionally rebased based on this max value."""

    # Calculate the max value out of this function.
    # May not even end up being used; Pandas probably has a more efficient df version of this.

    gtisr_norm = float(gtisr_singlescore / max_gtisr_val) * 100

    return gtisr_norm


def gtiratio_calculator(dma_gtis, dma_ccadmdnorm, uoa_ccadmdnorm, decimal_places=4):
    """This function will calculate a UOA-level Google Trends Interest Ratio (GTIR)
    using data from the ACS-defined CCAoA demand index
    and the Google Trends Metro Region (DMA) Google Trends Interest score (GTIS)."""

    uoa_gtir = float(float(dma_gtis * uoa_ccadmdnorm) / dma_ccadmdnorm)

    uoa_gtir = round(uoa_gtir, int(decimal_places))

    return uoa_gtir


def uncertainty_df_field(
    df, field, coverage_factor_k=2, observation_threshold=False, minimum_observations=30
):
    """This function will calculate the uncertainty based on the numeric values in a dataframe's specified column."""
    # # Calculate the average of the field
    # # # May not need this....
    # average = df[field].average()

    # Clean the target column to ensure any null values are treated as such
    df[field] = (
        df[field]
        .astype(str)
        .str.upper()
        .replace("", np.nan)
        .replace("NULL", np.nan)
        .replace("N/A", np.nan)
        .replace("(BLANK)", np.nan)
        .replace("NAN", np.nan)
    ).astype(float)
    non_null_counts = df[field].count()

    # Calculate the standard deviation.
    std_dev = df[field].std()

    # Ensure numeric input arguments
    # # Would be better with python argument typing, but I'm not there yet.
    coverage_factor_k = int(float(coverage_factor_k))
    minimum_observations = int(float(minimum_observations))

    if (observation_threshold is False) or (
        observation_threshold is True and non_null_counts >= minimum_observations
    ):
        # Calculate the uncertainty with a defined coverage factor (K)
        # # =(std_dev/SQRT(COUNT(F7:F1048576)))*2
        uncertainty = float((float(std_dev) / float(math.sqrt(float(non_null_counts)))) * float(coverage_factor_k))
        return uncertainty
    else:
        # The minimum records required to calculate uncertainty have not been acquired.
        # Record more data samples and try again.
        return None
