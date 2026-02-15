@echo off
REM Telegram Code Generation Bot Starter
REM This script ensures only one bot instance is running

echo Checking for existing bot processes...

REM Kill any existing Python processes
taskkill /FI "WINDOWTITLE eq python main.py*" /T /F 2>nul

REM Also kill by checking for python.exe running from this directory
for /f "tokens=2" %%A in ('tasklist /FI "IMAGENAME eq python.exe" ^| find /C "python"') do (
    if %%A GTR 0 (
        echo Stopping existing Python processes...
        taskkill /IM python.exe /F 2>nul
        timeout /t 2 /nobreak
    )
)

echo.
echo Starting Telegram Code Generation Bot...
echo.

REM Start the bot
python main.py

REM If bot crashes, wait before closing window
if errorlevel 1 (
    echo.
    echo Bot encountered an error. Check .env file and try again.
    echo Press any key to close...
    pause
)
