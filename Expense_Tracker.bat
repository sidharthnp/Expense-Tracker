@echo off
title Expense Tracker with SwishFormer Environment
echo Activating SwishFormer conda environment...

REM Initialize conda for batch script
call "C:\Users\HP\anaconda3\Scripts\activate.bat"

REM Activate the SwishFormer environment
call conda activate SwishFormer

REM Check if environment activation was successful
if errorlevel 1 (
    echo ERROR: Failed to activate SwishFormer environment!
    echo Make sure the environment exists and conda is properly installed.
    pause
    exit /b 1
)

echo SwishFormer environment activated successfully!
echo.

REM Change to your Expense Tracker directory
cd /d "C:\Users\HP\Desktop\Expense tracker"

REM Check if expense_tracker.py exists
if not exist "expense_tracker.py" (
    echo ERROR: expense_tracker.py not found in the Expense Tracker folder!
    pause
    exit /b 1
)

REM Run expense_tracker.py with the activated SwishFormer environment
echo Running expense_tracker.py with SwishFormer environment...
echo.
python expense_tracker.py

REM Check if the script ran successfully
if errorlevel 1 (
    echo.
    echo An error occurred while running expense_tracker.py
    echo The error details should be shown above.
) else (
    echo.
    echo Expense Tracker finished successfully.
)

echo.
echo Press any key to close this window...
pause

REM Deactivate the environment (optional, as the window will close anyway)
call conda deactivate
