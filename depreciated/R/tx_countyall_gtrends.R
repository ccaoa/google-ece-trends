# Init Stats Testing for Maine's 2021 Nemours data at the provider level.
library(readxl)
# targsheet="4rollup"
fragpth="OneDrive - NACCRRA\\Documents\\ArcGIS\\Projects\\GoogleTrendsDemandTestProject\\gtrends_data\\AGOL_Exports\\tx_alldmacounty_5_dmagtis.xls"
fullpath = file.path(
  (Sys.getenv("USERPROFILE")),fragpth, fsep="\\")
fullread=read_excel(fullpath)#,sheet = targsheet)

# T Tests
# GTIR ~ Bowtie
t.test(fullread$gtirat_rebase,(fullread$avgnsearch/fullread$total_pop))
# GTIR ~ Bowtie
t.test(fullread$gtir_cincy_rebase,(fullread$avgnsearch/fullread$total_pop))
# Bowtie Searches ~ CCA_DMD_Norm
t.test(fullread$ccadmdnorm,fullread$avgnsearch)
# Bowtie Searches ~ GTrends
t.test(fullread$txonly_n_1,fullread$gtis_st_av)

#linear_toc_model_maine = lm(me_prov_read$cacfp ~ me_prov_read$Type_Of_Program)
linear_toc_model_maine = lm(me_prov_read$cacfp ~ me_prov_read$ccc + me_prov_read$fcc+me_prov_read$nursery)
summary(linear_toc_model_maine)
# FCCs are statistically significantly more likely to support CACFP than CCCs.

linear_model_capcontrol = lm(me_prov_read$cacfp ~ me_prov_read$License_Capacity+me_prov_read$ccc + me_prov_read$fcc+me_prov_read$nursery)
summary(linear_model_capcontrol)
