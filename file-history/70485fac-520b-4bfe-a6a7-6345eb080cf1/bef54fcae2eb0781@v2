@echo off
echo ============================================================ > C:\users\crossover\diagnosis.log
echo Environment Diagnosis >> C:\users\crossover\diagnosis.log
echo ============================================================ >> C:\users\crossover\diagnosis.log
echo. >> C:\users\crossover\diagnosis.log

echo Testing Python... >> C:\users\crossover\diagnosis.log
"C:\Program Files\Python312\python.exe" --version >> C:\users\crossover\diagnosis.log 2>&1
echo. >> C:\users\crossover\diagnosis.log

echo Testing NumPy import... >> C:\users\crossover\diagnosis.log
"C:\Program Files\Python312\python.exe" -c "import numpy; print('NumPy version:', numpy.__version__)" >> C:\users\crossover\diagnosis.log 2>&1
echo. >> C:\users\crossover\diagnosis.log

echo Testing MetaTrader5 import... >> C:\users\crossover\diagnosis.log
"C:\Program Files\Python312\python.exe" -c "import MetaTrader5; print('MetaTrader5 version:', MetaTrader5.__version__)" >> C:\users\crossover\diagnosis.log 2>&1
echo. >> C:\users\crossover\diagnosis.log

echo Testing pandas import... >> C:\users\crossover\diagnosis.log
"C:\Program Files\Python312\python.exe" -c "import pandas; print('pandas version:', pandas.__version__)" >> C:\users\crossover\diagnosis.log 2>&1
echo. >> C:\users\crossover\diagnosis.log

echo Testing pandas-ta import... >> C:\users\crossover\diagnosis.log
"C:\Program Files\Python312\python.exe" -c "import pandas_ta; print('pandas-ta version:', pandas_ta.version)" >> C:\users\crossover\diagnosis.log 2>&1
echo. >> C:\users\crossover\diagnosis.log

echo ============================================================ >> C:\users\crossover\diagnosis.log
echo Diagnosis complete. Check C:\users\crossover\diagnosis.log >> C:\users\crossover\diagnosis.log
echo ============================================================ >> C:\users\crossover\diagnosis.log

echo Diagnosis complete. Output written to C:\users\crossover\diagnosis.log
echo.
type C:\users\crossover\diagnosis.log
echo.
pause
