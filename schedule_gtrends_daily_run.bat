echo Setting up a daily execution of the Google Trends Child Care Workflow.

:: set "CUR_DIR=%~dp0"
set "GTRENDS_DIR=%~dp0"
:: echo "%GTRENDS_DIR%"

:: Schedule the task
:: Quotations must be in this format b/c of Windows path spaces: https://stackoverflow.com/a/17079439/15517267
schtasks /create /tn gtrends /sc daily /st 14:22 /tr "'%GTRENDS_DIR%datapulls22.bat'"
:: See the results of this assignment
schtasks /query /tn gtrends /v /fo list
