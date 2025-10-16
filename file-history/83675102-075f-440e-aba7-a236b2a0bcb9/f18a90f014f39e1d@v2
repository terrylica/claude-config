@echo off
echo ============================================================
echo Installing pandas-ta for RSI Calculation
echo ============================================================
echo.

echo Installing pandas-ta package in Wine Python...
"C:\Program Files\Python312\python.exe" -m pip install pandas-ta
if errorlevel 1 (
    echo ERROR: Failed to install pandas-ta
    pause
    exit /b 1
)
echo.

echo Testing pandas-ta import...
"C:\Program Files\Python312\python.exe" -c "import pandas_ta; print('pandas-ta version:', pandas_ta.__version__)"
if errorlevel 1 (
    echo ERROR: pandas-ta import failed
    pause
    exit /b 1
)
echo.

echo ============================================================
echo pandas-ta Installation: SUCCESSFUL
echo ============================================================
echo Next: Create export script and test MT5 connection
echo.
pause
