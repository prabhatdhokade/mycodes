#!/bin/bash
# Cross-Platform Job Application Agent Runner
# Works on Mac, Linux, and WSL

echo "[TARGET] Job Application Agent - Cross-Platform Launcher"
echo "==============================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "[ERROR] Python is not installed or not in PATH"
        echo "Please install Python 3.8+ and add it to PATH"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check if we're in the right directory
if [ ! -f "optimized_main.py" ]; then
    echo "[ERROR] optimized_main.py not found"
    echo "Please run this script from the job_application_agent directory"
    exit 1
fi

# Show menu
echo ""
echo "[START] Available Options:"
echo "1. [TARGET] Start intelligent hunting (automated)"
echo "2. [SEARCH] Run single hunt session"
echo "3. [STATUS] Check hunter status"
echo "4. [USER] Show hunter profile"
echo "5. [FORM] Test smart form answers"
echo "6. [CONFIG] Run diagnostics"
echo "7. [WEB] Hunt on Naukri only"
echo "8. [WEB] Hunt on LinkedIn only"
echo "9. [AI] Interactive mode"
echo "0. Exit"

read -p "Enter your choice (0-9): " choice

case $choice in
    1)
        $PYTHON_CMD optimized_main.py --hunt
        ;;
    2)
        $PYTHON_CMD optimized_main.py --hunt-once
        ;;
    3)
        $PYTHON_CMD optimized_main.py --status
        ;;
    4)
        $PYTHON_CMD optimized_main.py --profile
        ;;
    5)
        $PYTHON_CMD optimized_main.py --test-forms
        ;;
    6)
        $PYTHON_CMD optimized_main.py --diagnose
        ;;
    7)
        $PYTHON_CMD optimized_main.py --hunt-once --platform naukri
        ;;
    8)
        $PYTHON_CMD optimized_main.py --hunt-once --platform linkedin
        ;;
    9)
        $PYTHON_CMD optimized_main.py
        ;;
    0)
        echo "[SUCCESS] Goodbye!"
        exit 0
        ;;
    *)
        echo "[ERROR] Invalid choice"
        ;;
esac

echo ""
read -p "Press Enter to continue..."