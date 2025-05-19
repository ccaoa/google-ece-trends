# Init Stats Testing for Maine's 2021 Nemours data at the provider level.
library(readxl)
# targsheet="4rollup"
# fragpth="Downloads\\tx_alldmacounty_5_dmagtis.xls"
fullorpath = "C:\\Users\\Jacob.Cooper\\OneDrive - NACCRRA\\Documents\\ArcGIS\\Projects\\GoogleTrendsDemandTestProject\\gtrends_data\\AGOL_Exports\\or_counties_all_providerjoin.xls"
orfullread=read_excel(fullorpath)#,sheet = targsheet)

# T Tests
# USA GTIR ~ Pot. Enrollment
t.test(orfullread$gtir_usa_rbse,orfullread$enroll_percap)
# State Cincy GTIR ~ Pot. Enrollment
t.test(orfullread$gtir_cincy_rbse,orfullread$enroll_percap)
#^USA GTIR has a better t-value result (greater) than the cincy method, indicating it is the better fit. 
##"The t-value measures the size of the difference relative to the variation in your sample data. Put another way, T is simply the calculated difference represented in units of standard error. The greater the magnitude of T, the greater the evidence against the null hypothesis."
