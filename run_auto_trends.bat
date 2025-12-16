@echo off
title AngyOne - Autonomous Trend Engine (Running...)
color 0f
echo ========================================================
echo   AN.GY ONE - AUTONOMOUS NEWS ENGINE
echo ========================================================
echo.
echo [1/3] Initializing Environment...
cd /d "%~dp0"

echo [2/3] Running Trend Scraper and Content Generator...
echo       (Generating 1 News Article + Updating Menu...)
echo.
python scrapers/trend_engine.py

echo.
echo [3/3] Sync complete. Check above for errors.
echo.
echo ========================================================
echo   DONE. Your site is live.
echo ========================================================
pause
