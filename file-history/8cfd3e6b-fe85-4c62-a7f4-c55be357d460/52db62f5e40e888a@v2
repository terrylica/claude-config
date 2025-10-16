@echo off
echo ============================================================
echo Installing mt5linux Bridge Package
echo ============================================================
echo.

echo Installing mt5linux package in Wine Python...
"C:\Program Files\Python312\python.exe" -m pip install mt5linux
if errorlevel 1 (
    echo ERROR: Failed to install mt5linux
    pause
    exit /b 1
)
echo.

echo ============================================================
echo mt5linux Installation: SUCCESSFUL
echo ============================================================
echo Next step: Install mt5linux on macOS
echo   Command: uv pip install mt5linux
echo.
pause
