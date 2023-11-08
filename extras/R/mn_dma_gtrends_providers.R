# Init Stats Testing for Maine's 2021 Nemours data at the provider level.
library(readxl)
# targsheet="4rollup"
# fragpth="Downloads\\tx_alldmacounty_5_dmagtis.xls"
dmamnpath = "C:\\Users\\Jacob.Cooper\\OneDrive - NACCRRA\\Documents\\ArcGIS\\Projects\\GoogleTrendsDemandTestProject\\gtrends_data\\AGOL_Exports\\mn_dma_providerjoin.xls"
mndmaread=read_excel(dmamnpath)#,sheet = targsheet)

# T Tests
# GTIS ~ CCA DMD Norm
t.test(mndmaread$ccadmdnorm,mndmaread$gtis_us_avg)
# OR raw potential damand ~ Pot. Enrollment
t.test(mndmaread$cca_demand_stonly,mndmaread$tot_enroll)
# USA GTIS ~ Pot. Enrollment
t.test(mndmaread$gtis_us_avg,(mndmaread$tot_enroll/mndmaread$total_pop_stonly))
# State GTIS (pre-Cincy) ~ Pot. Enrollment
t.test(mndmaread$gtis_st_avg,(mndmaread$tot_enroll/mndmaread$total_pop_stonly))
#^USA GTIS has a better t-value result (greater) than the state only GTIS, indicating it is the better fit. 
##"The t-value measures the size of the difference relative to the variation in your sample data. Put another way, T is simply the calculated difference represented in units of standard error. The greater the magnitude of T, the greater the evidence against the null hypothesis."

# Regressions
# OR raw potential damand ~ Pot. Enrollment
summary(lm(mndmaread$cca_demand_stonly~mndmaread$tot_enroll))#+mndmaread$total_pop_stonly))
