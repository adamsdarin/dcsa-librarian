@echo off
:: Registers the declared schedule with Windows Task Scheduler.
::
:: The task definitions are generated from config/schedule.json, never written
:: by hand. Change the cadence there and re-run this.

set "PROJECT=%~dp0..\.."
pushd "%PROJECT%"

python custodian.py schedule --render schtasks --command "\"%PROJECT%\adapters\windows\run-scan.cmd\"" > "%TEMP%\dcsa-tasks.cmd"
if errorlevel 1 (
  echo Could not render the schedule.
  popd
  exit /b 1
)

echo The following tasks will be created:
echo.
type "%TEMP%\dcsa-tasks.cmd"
echo.
choice /m "Create these scheduled tasks"
if errorlevel 2 (
  echo Cancelled. Nothing was changed.
  popd
  exit /b 0
)

call "%TEMP%\dcsa-tasks.cmd"
del "%TEMP%\dcsa-tasks.cmd"
popd
echo.
echo Done. Review them in Task Scheduler under Task Scheduler Library.
