@echo off
chcp 65001 > nul
cls
echo =====================================
echo 📊 투자설정 데이터 수집 테스트
echo =====================================
echo.
echo 주요 종목 10개만 수집합니다:
echo - 삼성전자, SK하이닉스, 카카오, 네이버
echo - 현대차, LG화학, 삼성SDI, LG
echo - KB금융, 신한지주
echo.
echo 시작하려면 아무 키나 누르세요...
pause > nul

echo.
echo 🚀 데이터 수집을 시작합니다...
echo.

python collect_investment_data.py --major

echo.
echo =====================================
echo 작업이 완료되었습니다!
echo =====================================
pause