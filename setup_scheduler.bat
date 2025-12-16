@echo off
title AngyOne - Setup 24/7 Scheduler
color 0a
echo ===================================================
echo   Setting up 24/7 Automatic Article Generation
echo ===================================================
echo.

:: Get the current directory
set SCRIPT_PATH=%~dp0run_auto_trends.bat

echo Script Path: %SCRIPT_PATH%
echo.

:: Create a scheduled task to run every 2 hours
schtasks /create /tn "AngyOne_TrendEngine" /tr "%SCRIPT_PATH%" /sc HOURLY /mo 2 /f

echo.
echo ===================================================
echo   DONE! Task Scheduler configured.
echo   - Task Name: AngyOne_TrendEngine
echo   - Schedule: Every 2 hours
echo   - Result: ~12 articles per day
echo ===================================================
echo.
echo To verify: Open Task Scheduler and look for "AngyOne_TrendEngine"
echo To stop: Run "schtasks /delete /tn AngyOne_TrendEngine /f"
echo.
pause
