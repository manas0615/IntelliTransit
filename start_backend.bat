@echo off
REM ===========================================================================
REM IntelliTransit: Backend Server Startup Script for Windows
REM ===========================================================================

set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

echo ===================================================
echo Starting IntelliTransit Backend Server...
echo URL: http://localhost:5000
echo ===================================================

if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe backend\run.py
) else (
    python backend\run.py
)
