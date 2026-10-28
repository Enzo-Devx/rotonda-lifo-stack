@echo off
setlocal
cd /d "%~dp0"
title Workbench - Website checks
if not exist ".venv\Scripts\python.exe" goto missing_setup
".venv\Scripts\python.exe" -m unittest discover -s tests -v
set "WORKBENCH_RESULT=%ERRORLEVEL%"
echo.
pause
exit /b %WORKBENCH_RESULT%
:missing_setup
echo Run SETUP_WINDOWS.bat first.
pause
exit /b 1
