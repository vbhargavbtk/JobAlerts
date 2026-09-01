@echo off
TITLE Personal Government Job Notification Intelligence Server
echo ======================================================================
echo STARTING PERSONAL GOVERNMENT JOB INTELLIGENCE ENGINE
echo ======================================================================
echo.
if exist .venv\Scripts\python.exe (
    echo [INFO] Activating virtual environment...
    .venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
) else (
    echo [INFO] Running with system python...
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
)
pause
