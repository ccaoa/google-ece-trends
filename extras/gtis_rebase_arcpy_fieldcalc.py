def gtiratio_normalizer(county_gtir, max_gtir_val=55.13899994):
    """This function will normalize the county-level Google Trends Intrest Ratio (GTIR)
    in ArcGIS Pro's  Field Calculator using by taking the maximum county_gtir and
    setting it = to 100. All other scores are proportionally weighted based on this value.
    """

    # Hard Code the max for now b/c ArcGIS Field Calculator is stupid
    # # Found this value by calling "Statistics" in the attribute table.
    # max_gtir_val_or = 122.541053772
    # max_gtir_val_usa = 71.4122085571
    # # Switch these if wanting to try the other value.
    max_gtir_val = max_gtir_val  # _usa  # max_gtir_val_or  #

    county_gtir_norm = float(county_gtir / max_gtir_val) * 100

    return county_gtir_norm


# gtiratio_normalizer(!gtirat_usa!)
