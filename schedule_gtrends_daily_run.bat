echo Setting up a daily execution of the Google Trends Child Care Workflow.

:: set "CUR_DIR=%~dp0"
set "GTRENDS_DIR=%~dp0"
:: echo "%GTRENDS_DIR%"

:: Schedule the task
schtasks /create /tn gtrends /sc daily /st 2:22 /tr "'%GTRENDS_DIR%\datapulls22.bat'"
schtasks /query /tn gtrends /v /fo list
