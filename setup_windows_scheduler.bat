@echo off
echo File Scheduler - Windows Task Scheduler Setup
echo ==========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and ensure it's in your system PATH
    pause
    exit /b 1
)

REM Check if the Python script exists
if not exist "file_scheduler_persistent.py" (
    echo ERROR: file_scheduler_persistent.py not found
    echo Please ensure the script is in the current directory
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

echo Available operations:
echo 1. Install dependencies
echo 2. Test configuration
echo 3. Run GUI application
echo 4. Test batch mode
echo 5. View Windows tasks
echo 6. Exit
echo.

set /p choice="Select option (1-6): "

if "%choice%"=="1" goto install_deps
if "%choice%"=="2" goto test_config
if "%choice%"=="3" goto run_gui
if "%choice%"=="4" goto test_batch
if "%choice%"=="5" goto view_tasks
if "%choice%"=="6" goto exit
echo Invalid choice
pause
goto start

:install_deps
echo Installing dependencies...
pip install schedule
echo.
echo Dependencies installed successfully!
pause
goto start

:test_config
echo Testing configuration...
echo Disconnecting any previous connections...
net use \\172.31.18.136 /delete >nul 2>&1
net use Z: /delete >nul 2>&1

echo Mapping network share...
net use Z: \\172.31.18.136\ftp_user1 /user:ftp_user1 dummyPass
if errorlevel 1 (
    echo ERROR: Failed to map network drive Z:
    pause
    goto start
)
echo Testing batch mode...
python file_scheduler_persistent.py --batch

echo Disconnecting network share...
net use Z: /delete

echo.
echo Configuration test completed
pause
goto start

:run_gui
echo Starting GUI application...
python file_scheduler_persistent.py
goto exit

:test_batch
echo Disconnecting any previous connections...
net use \\172.31.18.136 /delete >nul 2>&1
net use Z: /delete >nul 2>&1

echo Mapping network share...
net use Z: \\172.31.18.136\ftp_user1 /user:ftp_user1 dummyPass
if errorlevel 1 (
    echo ERROR: Failed to map network drive Z:
    pause
    goto start
)
echo Testing batch mode...
python file_scheduler_persistent.py --batch

echo Disconnecting network share...
net use Z: /delete

echo.
echo Batch test completed
pause
goto start

:view_tasks
echo Opening Windows Task Scheduler...
taskschd.msc
goto start

:start
cls
goto main

:exit
echo.
echo Setup completed. You can now:
echo 1. Run the GUI: python file_scheduler_persistent.py
echo 2. Create Windows tasks through the application
echo 3. Monitor tasks in Windows Task Scheduler (taskschd.msc)
echo.
pause

:main
