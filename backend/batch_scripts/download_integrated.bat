@echo off
echo ============================================================
echo Kiwoom INTEGRATED Data Download
echo ============================================================
echo.
echo This will download EVERYTHING in ONE FILE per stock:
echo.
echo [PRICE DATA]
echo   - 10 years daily OHLCV
echo.
echo [TECHNICAL INDICATORS]
echo   - Moving Averages: MA5, MA10, MA20, MA60, MA120
echo   - Volume MA: VOL_MA5, VOL_MA20
echo   - RSI (14 days)
echo   - MACD (12-26-9)
echo   - Bollinger Bands
echo   - Stochastic (14 days)
echo   - ATR, OBV
echo.
echo [FINANCIAL DATA]
echo   - PER, PBR, ROE, EPS, BPS
echo   - Revenue, Operating Profit, Net Income
echo   - Debt Ratio, Current Ratio
echo   - Market Cap
echo.
echo Output: D:\Dev\auto_stock\data\integrated\
echo Format: [CODE]_[NAME]_integrated.csv
echo.
echo Estimated time: 10-12 hours for all stocks
echo.
pause

cd /d D:\Dev\auto_stock\backend

REM Install pandas if needed
C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe -m pip install pandas

REM Clean old data
echo.
echo Cleaning old data...
rmdir /s /q D:\Dev\auto_stock\data\kiwoom 2>nul
rmdir /s /q D:\Dev\auto_stock\data\kiwoom_10years 2>nul

REM Run integrated download
C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe download_all_integrated.py

echo.
echo Integrated Download Complete!
pause