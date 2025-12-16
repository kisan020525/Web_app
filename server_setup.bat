@echo off
title AngyOne Server Setup (AWS)
color 0a

echo ===================================================
echo   AngyOne Autopilot - Server Configuration
echo ===================================================
echo.
echo [1/4] Installing Python Dependencies...
pip install google-generativeai pandas requests pytrends
echo.

echo [2/4] Configuring Git for Automated Push...
git config --global credential.helper store
echo * IMPORTANT: The first time you push, you will be asked for credentials.
echo * After that, they will be saved forever.
echo.

echo [3/4] Creating Scheduled Task (Hourly Trend Check)...
echo * You can create a task manually in Task Scheduler to run 'run_auto_trends.bat'
echo * Recommended Schedule: Every 2 Hours.
echo.

echo [4/4] Verifying Setup...
python --version
pip --version
echo.
echo ===================================================
echo   SETUP COMPLETE!
echo   1. Run 'run_auto_trends.bat' once manually.
echo   2. Sign in to GitHub when prompted.
echo   3. Set up Task Scheduler.
echo ===================================================
pause
