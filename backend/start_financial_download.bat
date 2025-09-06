@echo off
echo ============================================================
echo 키움 재무제표 다운로드 (분기별, 연도별)
echo ============================================================
echo.
echo 【분기별 재무제표】
echo   - 최근 5년 (20개 분기)
echo   - 손익계산서: 매출액, 영업이익, 당기순이익
echo   - 재무상태표: 자산총계, 부채총계, 자본총계
echo   - 재무비율: ROE, ROA, 부채비율, 유동비율
echo   - 주당지표: EPS, BPS
echo.
echo 【연도별 재무제표】
echo   - 최근 10년
echo   - 손익계산서 (연간 전체)
echo   - 재무상태표 (연말 기준)
echo   - 현금흐름표
echo   - 성장률: 매출액, 영업이익, 순이익 증가율
echo.
echo 저장 위치:
echo   - 분기별: D:\Dev\auto_stock\data\financial_statements\quarterly
echo   - 연도별: D:\Dev\auto_stock\data\financial_statements\yearly
echo.
pause

REM 32비트 Python으로 실행
C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe download_financial_statements.py

echo.
echo 재무제표 다운로드 완료!
pause