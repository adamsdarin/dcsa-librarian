@echo off
setlocal enabledelayedexpansion
:: Local scan wrapper for Windows Task Scheduler.
::
:: Runs entirely on this machine: stdlib Python, no model, no cloud runner, no
:: service. DCSA blocks hosted CI runners, so the scan has to originate from an
:: ordinary desktop connection.
::
:: Edit the three settings below for this machine, then register the tasks with
:: adapters\windows\install-tasks.cmd

set "PROJECT=%~dp0..\.."
set "LIBRARY=%USERPROFILE%\Documents\DCSA Library"
set "ALERTS=%USERPROFILE%\Desktop"

if "%~1"=="" (
  echo Usage: run-scan.cmd ^<job-id^>
  echo Jobs are declared in config\schedule.json
  exit /b 64
)

pushd "%PROJECT%"
python custodian.py scheduled-scan --job %~1 --library "%LIBRARY%"
set "CODE=%ERRORLEVEL%"
popd

set "REPORT=%PROJECT%\state\reports\%~1-latest.txt"

:: Put the report somewhere it cannot be missed. Task Scheduler also shows the
:: exit code as "Last Run Result": 0 clean, 1 incomplete, 3 findings.
if "%CODE%"=="3" copy /y "%REPORT%" "%ALERTS%\DCSA-SCAN-FINDINGS.txt" >nul
if "%CODE%"=="1" copy /y "%REPORT%" "%ALERTS%\DCSA-SCAN-INCOMPLETE.txt" >nul

exit /b %CODE%
