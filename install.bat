@echo off
setlocal enabledelayedexpansion

title Installing InRat Planner
echo ========================================
echo        INSTALLING InRat Planner
echo ========================================
echo.

set PYTHON_EXE=python
set VENV_DIR=venv
set REQUIREMENTS=requirements.txt

:: Check Python version
echo Checking Python version...
%PYTHON_EXE% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    echo Please install Python 3.12 or higher
    echo Download from: https://python.org/downloads/
    pause
    exit /b 1
)

:: Get Python version and check if it's 3.12 or higher
for /f "tokens=2 delims=. " %%i in ('%PYTHON_EXE% --version 2^>^&1') do set PY_MAJOR=%%i
for /f "tokens=3 delims=. " %%i in ('%PYTHON_EXE% --version 2^>^&1') do set PY_MINOR=%%i

if "%PY_MINOR%"=="" set PY_MINOR=0

echo Found Python version: %PY_MAJOR%.%PY_MINOR%

:: Check if version is 3.12 or higher
if %PY_MAJOR% LSS 3 (
    echo ERROR: Python version must be 3.12 or higher
    echo Current version: %PY_MAJOR%.%PY_MINOR%
    echo Please install Python 3.12 or higher
    pause
    exit /b 1
)

if %PY_MAJOR% EQU 3 (
    if %PY_MINOR% LSS 12 (
        echo ERROR: Python version must be 3.12 or higher
        echo Current version: 3.%PY_MINOR%
        echo Please install Python 3.12 or higher
        pause
        exit /b 1
    )
)

echo Python version check passed: %PY_MAJOR%.%PY_MINOR%

:: Check if requirements.txt exists
if not exist "%REQUIREMENTS%" (
    echo ERROR: File %REQUIREMENTS% not found
    echo Requirements file %REQUIREMENTS% not found!
    pause
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
if exist "%VENV_DIR%" (
    echo Virtual environment already exists, deleting...
    rmdir /s /q "%VENV_DIR%" 2>nul
)

%PYTHON_EXE% -m venv "%VENV_DIR%"
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    echo Failed to create virtual environment!
    pause
    exit /b 1
)
echo Virtual environment created successfully

:: Activate virtual environment
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate"
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    echo Failed to activate virtual environment!
    pause
    exit /b 1
)

:: Update pip
echo Updating pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo WARNING: Failed to update pip, continuing...
)

:: Install dependencies
echo Installing dependencies from %REQUIREMENTS%...
echo Installing dependencies, this may take a few minutes...
python -m pip install -r "%REQUIREMENTS%"
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo Error installing dependencies!
    echo.
    echo Try the following solutions:
    echo 1. Run install.bat as Administrator
    echo 2. Check your internet connection
    echo 3. Make sure antivirus is not blocking installation
    echo ========================================
    echo.
    pause
    exit /b 1
)
echo Dependencies installed successfully

:: start.bat
echo @echo off > start.bat
echo call %VENV_DIR%\Scripts\activate >> start.bat
echo python src\main.py >> start.bat
echo pause >> start.bat

:: Final message
echo Installation completed successfully!
echo.
echo ========================================
echo    INSTALLATION COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo What's next?
echo Run start.bat to start working
echo.

:: Auto close after 30 seconds
choice /c yn /t 30 /d y /m "Close window now? (Y - yes, N - keep open)"
if %errorlevel% equ 1 (
    exit /b 0
) else (
    echo Window kept open
)

endlocal