def gtiratio_calculator(dma_gtis, dma_ccadmdnorm, county_ccadmdnorm, decimal_places=4):
    """This function will calculate the county-level Google Trends Intrest Ratio (GTIR)
    in ArcGIS Pro's  Field Calculator using data from the ACS-definded CCAoA demand index
    and the Google Trends Metro Region (DMA) Google Trends Interest score (GTIS)"""

    county_gtir = float(float(dma_gtis * county_ccadmdnorm) / dma_ccadmdnorm)

    county_gtir = round(county_gtir, int(decimal_places))

    return county_gtir


# gtiratio_calculator(!gtisorfeb20_21!,!ccadmdnorm_1!,!ccadmdnorm!)
# gtiratio_calculator(!gtis_st_avg!,!dma_ccadmdnorm!,!ccadmdnorm!)
