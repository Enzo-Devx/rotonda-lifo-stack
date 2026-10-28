@echo off
setlocal
cd /d "%~dp0"
title Workbench - First-time setup
echo.
echo WORKBENCH - FIRST-TIME SETUP
echo You need Python 3.10 or newer and an internet connection for this step.
echo.
set "WORKBENCH_PY="
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if not errorlevel 1 set "WORKBENCH_PY=py -3"
if defined WORKBENCH_PY goto python_ready
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if not errorlevel 1 set "WORKBENCH_PY=python"
if defined WORKBENCH_PY goto python_ready
echo Python 3.10 or newer was not found.
echo Install Python from https://www.python.org/downloads/
echo Select "Add Python to PATH" in the installer, then reopen this file.
echo.
pause
exit /b 1
:python_ready
if exist ".venv\Scripts\python.exe" goto install_packages
echo Creating a local Python environment...
%WORKBENCH_PY% -m venv .venv
if errorlevel 1 goto setup_failed
:install_packages
echo Installing Flask...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto setup_failed
".venv\Scripts\python.exe" -c "import flask, sqlite3; from backend.app import create_app; print('Flask, SQLite, and backend imports are ready.')"
if errorlevel 1 goto setup_failed
echo.
echo SETUP COMPLETE
echo Double-click START_WEBSITE.bat to open your website.
echo Keep frontend, backend, and database together in this folder.
echo Student Stack file: backend\stack.py
echo Database file is created automatically at database\data\workbench.sqlite3.
echo.
pause
exit /b 0
:setup_failed
echo.
echo Setup did not finish. Read the error above.
echo Check your internet connection and Python installation, then try again.
echo.
pause
exit /b 1
