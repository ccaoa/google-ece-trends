# GTIR based on USA_DMA_GTIS
# # See the gitr_arcpy_fieldcalc.py for the function version of this
# (!gtis_us_avg! *!ccadmdnorm! )/!ccadmdnorm_dma_all!

# GTIR based on DMA_GTIS_StOnly_Cincy
# # !! Select only counties in target state for this calc !!
def gtiratio_calculator(
    dma_state_gtis,
    dma_ccadmd_stonlycounties,
    dma_totalpop_allcounties,
    county_ccadmdnorm,
    dma_ccadmdnorm,
    st_field,
    targ_st_abv,
    decimal_places=4,
):
    """This function will calculate the county-level Google Trends Intrest Ratio (GTIR)
    in ArcGIS Pro's  Field Calculator using data from the ACS-definded CCAoA demand index
    and the Google Trends Metro Region (DMA) Google Trends Interest score (GTIS).
     It employs the Cincinnati Method intended to correct for imbalances inherent within Google State-level
      Interest Scores that disadvantages multi-state DMAs"""
    if st_field.lower() == targ_st_abv.lower():
        # Only caculate a Cincy GTIR value for states within the target state
        # # OG GTIR Formula:
        # #county_gtir = float(float(gtmr_gtis * county_ccadmdnorm) / gtmr_ccadmdnorm)

        # Calc. a skewed CCA Demand value where you can normalize out the already - skewed DMA_State_GTIS
        dma_ccadmdskew_cincy = float(dma_ccadmd_stonlycounties) / float(
            dma_totalpop_allcounties
        )
        cincy_gtir = (
            (float(dma_state_gtis) / dma_ccadmdskew_cincy) * float(county_ccadmdnorm)
        ) / float(dma_ccadmdnorm)
        cincy_gtir = round(cincy_gtir, int(decimal_places))

        return cincy_gtir
    else:
        return None


# ((!gtis_st_avg!/!ccadmdnorm_stonly!)*!ccadmdnorm!)/!ccadmdnorm_dma_all!
