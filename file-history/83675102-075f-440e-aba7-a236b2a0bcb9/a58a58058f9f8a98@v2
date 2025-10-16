@echo off
del C:\users\crossover\mt5_test.log 2>nul
echo Running MT5 Connection Test... > C:\users\crossover\mt5_test.log
echo. >> C:\users\crossover\mt5_test.log
"C:\Program Files\Python312\python.exe" C:\users\crossover\test_mt5_connection.py >> C:\users\crossover\mt5_test.log 2>&1
echo. >> C:\users\crossover\mt5_test.log
type C:\users\crossover\mt5_test.log
pause
