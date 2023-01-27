:: PURPOSE: Automate runs of the `late2022_datapulls.py` file.
:: --------------------------------------------------
:: TESTING
::  https://serverfault.com/questions/95686/change-current-directory-to-the-batch-file-directory
:: To ID the current project directory:
::cd %~dp0
:: To ID the venv from the current project directory:
::echo "%~dp0py_venv\venv\Scripts\python.exe"
:: To log the results of a run:
:: --------------------------------------------------
:: EXECUTION
echo Starting Google Trends data pull.
:: There are two ways of executing this batch file from the cmd shell.
::  Each depends on accessing the file and directory paths correctly.
::
:: 1) Change the working path location to be the same directory as the py_venv subdirectory.
::cd %~dp0
:: Then execute the file.
::@py_venv\venv\Scripts\python.exe .\late2022_datapulls.py > .\log.txt
::
:: 2) Access each file relatively without changing directories.
@"%~dp0py_venv\venv\Scripts\python.exe" "%~dp0late2022_datapulls.py"  > "%~dp0log.txt"
:: --------------------------------------------------
:: AUTOMATION
:: You can now create automated runs of this batch file by using schtasks.
::  See https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks
:: Creation ex:
::schtasks /create /sc DAILY /tn gtrends /st 13:23 /tr "C:\Users\Jacob.Cooper\OneDrive - NACCRRA\Documents\ArcGIS\Projects\GoogleTrends_Demand_HomeDir\coding\google-ece-pytrends\datapulls22.bat"
:: Edit ex:
::schtasks /change /tn gtrends /st 14:34
:: NOTE: You may need to format your windows paths with a space like this to get it to work.
::schtasks /change /tn gtrends -tr "\"C:\Users\Jacob.Cooper\OneDrive - NACCRRA\Documents\ArcGIS\Projects\GoogleTrends_Demand_HomeDir\coding\google-ece-pytrends\datapulls22.bat""
:: --------------------------------------------------
:: REPORTING
:: The data are being stored in the log.txt, but we can print that to the console in a schtasks too.
type "%~dp0log.txt"
:: Don't close the cmd window until you've had a chance to check out the results.
pause
