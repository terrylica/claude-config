@echo off
echo ============================================================
echo Installing pandas-ta with NumPy 1.26.4 pinned
echo ============================================================
echo.

echo Step 1: Ensure NumPy 1.26.4 is locked...
"C:\Program Files\Python312\python.exe" -m pip install "numpy==1.26.4"
if errorlevel 1 (
    echo ERROR: Failed to install NumPy 1.26.4
    pause
    exit /b 1
)
echo.

echo Step 2: Installing pandas-ta with --no-deps first...
"C:\Program Files\Python312\python.exe" -m pip install --no-deps pandas-ta
if errorlevel 1 (
    echo ERROR: Failed to install pandas-ta (no deps)
    pause
    exit /b 1
)
echo.

echo Step 3: Installing pandas-ta dependencies (excluding numpy)...
"C:\Program Files\Python312\python.exe" -m pip install pandas
if errorlevel 1 (
    echo ERROR: Failed to install pandas
    pause
    exit /b 1
)
echo.

echo Step 4: Testing pandas-ta import...
"C:\Program Files\Python312\python.exe" -c "import pandas_ta; print('pandas-ta version:', pandas_ta.version)"
if errorlevel 1 (
    echo ERROR: pandas-ta import failed
    pause
    exit /b 1
)
echo.

echo Step 5: Verify NumPy version is still 1.26.4...
"C:\Program Files\Python312\python.exe" -c "import numpy; print('NumPy version:', numpy.__version__); assert numpy.__version__ == '1.26.4', 'NumPy version changed!'"
if errorlevel 1 (
    echo ERROR: NumPy version was overwritten!
    pause
    exit /b 1
)
echo.

echo ============================================================
echo SUCCESS: pandas-ta installed with NumPy 1.26.4
echo ============================================================
echo.
pause
