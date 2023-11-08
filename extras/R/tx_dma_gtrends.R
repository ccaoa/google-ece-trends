# # Init Stats Testing for GTrends data - TX DMA UOA
# library(readxl)
# targsheet="4rollup"
csvpth="C:\\Users\\Jacob.Cooper\\OneDrive - NACCRRA\\Documents\\ArcGIS\\Projects\\GoogleTrendsDemandTestProject\\gtrends_data\\AGOL_Exports\\tx_dma_gtrends_multistate_allcalcs.csv"
txdmaread=read.csv(csvpth)

# T Tests
# GTrends ~ CCA_DMD_Norm
t.test(txdmaread$gtis_st_av,(txdmaread$txonly_cca / txdmaread$txonly_tot))
# Bowtie Searches ~ CCA_DMD
t.test(txdmaread$txonly_n_1,txdmaread$txonly_cca)
# Bowtie Searches ~ GTrends
t.test(txdmaread$txonly_n_1,txdmaread$gtis_st_av)
# Bowtie Searches Normalized ~ GTrends
t.test((txdmaread$txonly_n_1/ txdmaread$txonly_tot),txdmaread$gtis_st_av)

#linear_toc_model_maine = lm(me_prov_read$cacfp ~ me_prov_read$Type_Of_Program)
linear_model = glm(txdmaread$gtis_st_av ~ (txdmaread$txonly_cca / txdmaread$txonly_tot))
summary(linear_model)
# FCCs are statistically significantly more likely to support CACFP than CCCs.

linear_model_capcontrol = lm(me_prov_read$cacfp ~ me_prov_read$License_Capacity+me_prov_read$ccc + me_prov_read$fcc+me_prov_read$nursery)
summary(linear_model_capcontrol)
