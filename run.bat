@echo off
rem =====================================================================
rem Reverse Engineer Skill — Windows Runner
rem =====================================================================
rem This script runs the pipeline smoothly on standard Windows CMD.
rem It avoids PowerShell execution policy blocks, automatically detects
rem Python, and forces UTF-8 encoding to prevent console crashes.
rem =====================================================================

setlocal enabledelayedexpansion

echo [info] Detecting Python environment...

rem Force Python to use UTF-8 encoding for standard Windows Command Prompt
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

rem Check for python
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PY_CMD=python
    goto :run
)

rem Check for python3
where python3 >nul 2>&1
if %errorlevel% equ 0 (
    set PY_CMD=python3
    goto :run
)

rem Check for py (Python launcher)
where py >nul 2>&1
if %errorlevel% equ 0 (
    set PY_CMD=py
    goto :run
)

echo [error] Python was not found on your system PATH.
echo [error] Please install Python (https://www.python.org/downloads/) and ensure
echo [error] the 'Add Python to PATH' option is checked during installation.
exit /b 1

:run
if "%~1"=="" (
    echo [error] No GitHub URL or local path provided.
    echo Usage: run.bat ^<github-repo-url-or-local-path^>
    echo Example: run.bat https://github.com/spring-projects/spring-petclinic
    exit /b 1
)

echo [info] Running Reverse Engineer Skill using %PY_CMD%...
%PY_CMD% "%~dp0reverse_engineer_skill.py" %*
exit /b %errorlevel%
