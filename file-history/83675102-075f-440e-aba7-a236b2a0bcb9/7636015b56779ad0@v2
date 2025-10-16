@echo off
echo ============================================================
echo Restoring NumPy 1.26.4 and Testing Environment
echo ============================================================
echo.

echo Step 1: Uninstalling all NumPy versions...
"C:\Program Files\Python312\python.exe" -m pip uninstall -y numpy
echo.

echo Step 2: Reinstalling NumPy 1.26.4...
"C:\Program Files\Python312\python.exe" -m pip install numpy==1.26.4
if errorlevel 1 (
    echo ERROR: Failed to install NumPy 1.26.4
    pause
    exit /b 1
)
echo.

echo Step 3: Reinstalling MetaTrader5...
"C:\Program Files\Python312\python.exe" -m pip install --force-reinstall --no-deps MetaTrader5
if errorlevel 1 (
    echo ERROR: Failed to reinstall MetaTrader5
    pause
    exit /b 1
)
echo.

echo Step 4: Testing MetaTrader5 import...
"C:\Program Files\Python312\python.exe" -c "import MetaTrader5; print('SUCCESS: MetaTrader5 version:', MetaTrader5.__version__)"
if errorlevel 1 (
    echo ERROR: MetaTrader5 import failed
    pause
    exit /b 1
)
echo.

echo Step 5: Installing pandas (for data manipulation)...
"C:\Program Files\Python312\python.exe" -m pip install --no-deps pandas
if errorlevel 1 (
    echo ERROR: Failed to install pandas
    pause
    exit /b 1
)
echo.

echo Step 6: Installing pandas dependencies (avoiding numpy upgrade)...
"C:\Program Files\Python312\python.exe" -m pip install python-dateutil pytz tzdata
if errorlevel 1 (
    echo ERROR: Failed to install pandas dependencies
    pause
    exit /b 1
)
echo.

echo Step 7: Testing pandas import...
"C:\Program Files\Python312\python.exe" -c "import pandas; print('pandas version:', pandas.__version__)"
if errorlevel 1 (
    echo ERROR: pandas import failed
    pause
    exit /b 1
)
echo.

echo Step 8: Verifying NumPy is still 1.26.4...
"C:\Program Files\Python312\python.exe" -c "import numpy; print('NumPy version:', numpy.__version__); assert numpy.__version__ == '1.26.4', 'NumPy upgraded!'"
if errorlevel 1 (
    echo ERROR: NumPy version changed!
    pause
    exit /b 1
)
echo.

echo ============================================================
echo Environment Restored Successfully!
echo ============================================================
echo - NumPy 1.26.4: OK
echo - MetaTrader5: OK
echo - pandas: OK
echo.
echo Note: We'll calculate RSI manually (simple code, no pandas-ta needed)
echo.
pause
