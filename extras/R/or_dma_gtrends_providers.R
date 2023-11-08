# Init Stats Testing for Maine's 2021 Nemours data at the provider level.
library(readxl)
# targsheet="4rollup"
# fragpth="Downloads\\tx_alldmacounty_5_dmagtis.xls"
dmaorpath = "C:\\Users\\Jacob.Cooper\\OneDrive - NACCRRA\\Documents\\ArcGIS\\Projects\\GoogleTrendsDemandTestProject\\gtrends_data\\AGOL_Exports\\or_dma_providerjoin.xls"
ordmaread=read_excel(dmaorpath)#,sheet = targsheet)

# T Tests
# GTIS ~ CCA DMD Norm
t.test(ordmaread$ccadmdnorm,ordmaread$gtis_us_avg)
# OR raw potential damand ~ Pot. Enrollment
t.test(ordmaread$cca_demand_stonly,ordmaread$enroll_pot)
# USA GTIS ~ Pot. Enrollment
t.test(ordmaread$gtis_us_avg,(ordmaread$enroll_pot/ordmaread$total_pop_stonly))
# State GTIS (pre-Cincy) ~ Pot. Enrollment
t.test(ordmaread$gtis_st_avg,(ordmaread$enroll_pot/ordmaread$total_pop_stonly))
#^USA GTIS has a better t-value result (greater) than the State GTIS, indicating it is the better fit. 
##"The t-value measures the size of the difference relative to the variation in your sample data. Put another way, T is simply the calculated difference represented in units of standard error. The greater the magnitude of T, the greater the evidence against the null hypothesis."

# Regressions
# OR raw potential damand ~ Pot. Enrollment
summary(lm(ordmaread$cca_demand_stonly~ordmaread$enroll_pot))