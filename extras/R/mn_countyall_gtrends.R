# Init Stats Testing for Maine's 2021 Nemours data at the provider level.
library(readxl)
# targsheet="4rollup"
# fragpth="Downloads\\tx_alldmacounty_5_dmagtis.xls"
fullmnpath = "C:\\Users\\Jacob.Cooper\\OneDrive - NACCRRA\\Documents\\ArcGIS\\Projects\\GoogleTrendsDemandTestProject\\gtrends_data\\AGOL_Exports\\mn_counties_all_providerjoin.xls"
mnfullread=read_excel(fullmnpath)#,sheet = targsheet)

# T Tests
# USA GTIR ~ Pot. Enrollment
t.test(mnfullread$gtir_usa_rbse,mnfullread$enroll_percap)#, na.action=na.omit())
# State Cincy GTIR ~ Pot. Enrollment
t.test(mnfullread$gtir_cincy_rbse,mnfullread$enroll_percap, na.action=na.fail())
#^USA GTIR has a much better t-value result (greater) than the cincy method, indicating it is the better fit. 
##"The t-value measures the size of the difference relative to the variation in your sample data. Put another way, T is simply the calculated difference represented in units of standard error. The greater the magnitude of T, the greater the evidence against the null hypothesis."
