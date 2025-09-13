@echo off
echo GitHub Personal Access Token 설정
echo.
echo 사용법: set_github_token.bat YOUR_PERSONAL_ACCESS_TOKEN
echo.

if "%1"=="" (
    echo Error: Personal Access Token을 입력해주세요.
    echo.
    echo 예시: set_github_token.bat ghp_xxxxxxxxxxxxxxxxxxxxx
    exit /b 1
)

set TOKEN=%1
set REPO_URL=https://%TOKEN%@github.com/khanyong/kyyquant-ai-solution.git

echo Token을 사용하여 remote URL 설정 중...
git remote set-url origin %REPO_URL%

echo.
echo 설정 완료! 이제 git push를 시도합니다...
git push -u origin feature/supabase-n8n-integration

echo.
echo 완료되었습니다.