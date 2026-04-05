@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   👁️  Starting AEye
echo ========================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Configuration file path
set "CONFIG_FILE=%USERPROFILE%\.aeye_config.json"

REM Check configuration file
if exist "%CONFIG_FILE%" (
    REM Try to read env_type using Python
    for /f "delims=" %%i in ('python -c "import json; import os; config = json.load(open(r'%CONFIG_FILE%')); print(config.get('env_type', 'system'))" 2^>nul') do (
        set "ENV_TYPE=%%i"
    )
    if "!ENV_TYPE!"=="" (
        set "ENV_TYPE=system"
    )
    echo Detected environment: !ENV_TYPE!
) else (
    echo No configuration file found, using system environment
    set "ENV_TYPE=system"
)

echo.

REM Launch based on environment type
if /i "!ENV_TYPE!"=="poetry" (
    echo Attempting to start with Poetry virtual environment...
    where poetry >nul 2>nul
    if !errorlevel! equ 0 (
        echo [OK] Poetry command found
        poetry run python -m aeye
        set "EXIT_CODE=!errorlevel!"
        if !EXIT_CODE! neq 0 (
            echo.
            echo [WARN] Poetry environment failed to start (exit code: !EXIT_CODE!^)
            echo.
            echo Would you like to use system environment instead? (y/n^)
            set /p "choice=Enter your choice: "
            if /i "!choice!"=="y" (
                echo.
                echo Starting with system environment...
                echo (No installation required, running via PYTHONPATH^)
                echo.
                call :check_and_install_dependencies
                if !errorlevel! equ 0 (
                    set "PYTHONPATH=%SCRIPT_DIR%"
                    python -m aeye
                )
            ) else (
                echo.
                echo Cancelled, not using system environment.
            )
        )
    ) else (
        echo [ERROR] Poetry command not found
        echo.
        echo Your configuration is set to use Poetry virtual environment,
        echo but Poetry is not installed on your system.
        echo.
        echo [DOC] Official Poetry installation guide:
        echo   https://python-poetry.org/docs/#installation
        echo.
        echo Install command (recommended^):
        echo   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing^).Content ^| python -
        echo.
        echo Would you like to use system environment instead? (y/n^)
        set /p "choice=Enter your choice: "
        if /i "!choice!"=="y" (
            echo.
            echo Starting with system environment...
            echo (No installation required, running via PYTHONPATH^)
            echo.
            call :check_and_install_dependencies
            if !errorlevel! equ 0 (
                set "PYTHONPATH=%SCRIPT_DIR%"
                python -m aeye
            )
        ) else (
            echo.
            echo Cancelled, not using system environment.
            echo Please install Poetry first and try again.
        )
    )
) else (
    echo Starting with system environment...
    echo (No installation required, running via PYTHONPATH^)
    echo.
    call :check_and_install_dependencies
    if !errorlevel! equ 0 (
        set "PYTHONPATH=%SCRIPT_DIR%"
        python -m aeye
    )
)

REM Keep window open to view errors
echo.
echo Press any key to close this window...
pause >nul
exit /b

REM ==========================================
REM Function to check and install dependencies
REM ==========================================
:check_and_install_dependencies
echo Checking dependencies...

REM Check PySide6
python -c "import PySide6" 2>nul
if !errorlevel! equ 0 (
    echo [OK] PySide6 is ready
) else (
    echo [WARN] PySide6 not found
    echo.
    echo AEye requires PySide6 to run the GUI interface.
    echo.
    echo Would you like to install PySide6 now? (y/n^)
    set /p "choice=Enter your choice: "
    if /i "!choice!"=="y" (
        echo.
        echo Installing PySide6...
        python -m pip install PySide6
        if !errorlevel! equ 0 (
            echo.
            echo [OK] PySide6 installed successfully!
            echo.
        ) else (
            echo.
            echo [ERROR] PySide6 installation failed!
            echo.
            echo Please run manually: pip install PySide6
            echo.
            exit /b 1
        )
    ) else (
        echo.
        echo Installation cancelled, cannot start AEye.
        echo.
        exit /b 1
    )
)
goto :eof
