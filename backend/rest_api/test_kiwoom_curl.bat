@echo off
echo ========================================
echo 키움 REST API 토큰 발급 테스트 (curl)
echo ========================================

set APP_KEY=iQ4uqUvLr7L-MPOaBxVZZs88uT-jGwVH
set APP_SECRET=9uBOq4tEp_Y2M1PBo1jQP3AiGBiZJfQ4bCyLT79RTaA=

echo.
echo 1. 키움증권 API 테스트
echo URL: https://openapi.kiwoom.com:9443/oauth2/token
curl -X POST "https://openapi.kiwoom.com:9443/oauth2/token" ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "grant_type=client_credentials" ^
  -d "appkey=%APP_KEY%" ^
  -d "appsecret=%APP_SECRET%" ^
  --connect-timeout 10

echo.
echo.
echo 2. 한국투자증권 API 테스트 (대체)
echo URL: https://openapi.koreainvestment.com:9443/oauth2/tokenP
curl -X POST "https://openapi.koreainvestment.com:9443/oauth2/tokenP" ^
  -H "Content-Type: application/json" ^
  -d "{\"grant_type\":\"client_credentials\",\"appkey\":\"%APP_KEY%\",\"appsecret\":\"%APP_SECRET%\"}" ^
  --connect-timeout 10

echo.
echo.
echo 완료!
pause