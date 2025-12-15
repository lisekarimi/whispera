@echo off
REM Build Windows executable script

REM Change to project root directory (parent of scripts/)
cd /d "%~dp0.."

echo Building Windows executable...
echo.

REM Check if uv is available
uv --version >nul 2>&1
if errorlevel 1 (
    echo Error: uv is not installed or not in PATH
    echo Please install uv from: https://github.com/astral-sh/uv
    pause
    exit /b 1
)

REM Sync dependencies (installs PyInstaller from pyproject.toml)
echo Syncing dependencies...
uv sync

REM Run the build script using uv
echo Building executable...
uv run python scripts/build_exe.py

if errorlevel 1 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build successful!
echo ========================================
echo Executable location: dist\Whispera.exe
echo.
echo IMPORTANT: Copy the .env file to the dist folder before running the exe!
echo.
pause
