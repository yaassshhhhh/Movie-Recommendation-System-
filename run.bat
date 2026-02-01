@echo off
title Movie Recommendation System
echo ===================================================
echo   Movie Recommendation System
echo ===================================================
echo.

echo [INFO] Checking dependencies (Flask, Pandas, Scikit-learn)...
:: Use python -m pip to bypass potential wrapper restrictions
python -m pip install flask pandas scikit-learn

echo.
echo [INFO] Starting Application...
python app.py

pause
