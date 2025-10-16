@echo off
echo ============================================================
echo Testing NumPy 1.26.4 Workaround for Wine UCRT Compatibility
echo ============================================================
echo.

echo [Step 1/4] Uninstalling existing NumPy...
"C:\Program Files\Python312\python.exe" -m pip uninstall -y numpy
if errorlevel 1 (
    echo ERROR: Failed to uninstall NumPy
    pause
    exit /b 1
)
echo.

echo [Step 2/4] Installing NumPy 1.26.4 (MetaTrader5 compatible version)...
"C:\Program Files\Python312\python.exe" -m pip install numpy==1.26.4
if errorlevel 1 (
    echo ERROR: Failed to install NumPy 1.26.4
    pause
    exit /b 1
)
echo.

echo [Step 3/4] Reinstalling MetaTrader5 package...
"C:\Program Files\Python312\python.exe" -m pip install --force-reinstall --no-deps MetaTrader5
if errorlevel 1 (
    echo ERROR: Failed to reinstall MetaTrader5
    pause
    exit /b 1
)
echo.

echo [Step 4/4] Testing MetaTrader5 import...
"C:\Program Files\Python312\python.exe" -c "import MetaTrader5 as mt5; print('SUCCESS: MetaTrader5 version:', mt5.__version__)"
if errorlevel 1 (
    echo ERROR: MetaTrader5 import failed
    echo This workaround did not resolve the issue.
    echo Next: Try Wine 10.1+ upgrade or native UCRT override.
    pause
    exit /b 1
)
echo.

echo ============================================================
echo Workaround Test: PASSED
echo ============================================================
echo MetaTrader5 package is now functional under Wine.
echo Next: Install mt5linux package for bridge setup.
echo.
pause
