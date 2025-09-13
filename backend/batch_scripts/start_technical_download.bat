@echo off
echo ============================================================
echo 키움 기술지표 다운로드 (종목별, 일별)
echo ============================================================
echo.
echo 다음 기술지표를 계산하여 저장합니다:
echo - 이동평균선 (MA): 5, 10, 20, 60, 120일
echo - 거래량 이동평균: 5, 20일
echo - RSI (상대강도지수): 14일
echo - MACD: 12-26-9
echo - 볼린저밴드: 20일 (상단/중단/하단)
echo - 스토캐스틱: 14일
echo - ATR (평균진폭): 14일
echo - OBV (거래량 지표)
echo.
echo 각 종목별로 일별 지표값이 CSV 파일로 저장됩니다.
echo 저장위치: D:\Dev\auto_stock\data\technical_indicators
echo.
pause

REM 32비트 Python으로 실행
C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe download_technical_indicators.py

echo.
echo 기술지표 다운로드 완료!
pause