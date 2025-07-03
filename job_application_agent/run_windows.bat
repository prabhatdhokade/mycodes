@echo off
:: Windows Job Application Agent Runner
:: Sets up proper Unicode support and runs the optimized version

echo [TARGET] Job Application Agent - Windows Launcher
echo ================================================

:: Set console to UTF-8
chcp 65001 > nul

:: Check if Python is available
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

:: Check if we're in the right directory
if not exist "optimized_main_windows.py" (
    echo [ERROR] optimized_main_windows.py not found
    echo Please run this script from the job_application_agent directory
    pause
    exit /b 1
)

:: Show menu
echo.
echo [START] Available Options:
echo 1. [TARGET] Start intelligent hunting (automated)
echo 2. [SEARCH] Run single hunt session
echo 3. [STATUS] Check hunter status
echo 4. [USER] Show hunter profile
echo 5. [FORM] Test smart form answers
echo 6. [CONFIG] Run diagnostics
echo 7. [WEB] Hunt on Naukri only
echo 8. [WEB] Hunt on LinkedIn only
echo 9. [AI] Interactive mode
echo 0. Exit

set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" (
    python optimized_main_windows.py --hunt
) else if "%choice%"=="2" (
    python optimized_main_windows.py --hunt-once
) else if "%choice%"=="3" (
    python optimized_main_windows.py --status
) else if "%choice%"=="4" (
    python optimized_main_windows.py --profile
) else if "%choice%"=="5" (
    python optimized_main_windows.py --test-forms
) else if "%choice%"=="6" (
    python optimized_main_windows.py --diagnose
) else if "%choice%"=="7" (
    python optimized_main_windows.py --hunt-once --platform naukri
) else if "%choice%"=="8" (
    python optimized_main_windows.py --hunt-once --platform linkedin
) else if "%choice%"=="9" (
    python optimized_main_windows.py
) else if "%choice%"=="0" (
    echo [SUCCESS] Goodbye!
    exit /b 0
) else (
    echo [ERROR] Invalid choice
)

echo.
pause