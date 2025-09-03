@echo off
setlocal enabledelayedexpansion

echo GitHub Token을 .env 파일에서 읽어옵니다...

rem .env 파일에서 GITHUB_TOKEN 찾기
for /f "tokens=1,2 delims==" %%a in (.env) do (
    if "%%a"=="GITHUB_TOKEN" (
        set TOKEN=%%b
        rem 공백과 주석 제거
        for /f "tokens=1" %%c in ("!TOKEN!") do set TOKEN=%%c
    )
)

if "!TOKEN!"=="" (
    echo.
    echo Error: .env 파일에 GITHUB_TOKEN이 설정되지 않았습니다.
    echo.
    echo 1. GitHub에서 Personal Access Token 생성:
    echo    https://github.com/settings/tokens
    echo.
    echo 2. .env 파일에 추가:
    echo    GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx
    echo.
    exit /b 1
)

echo Token 발견! Remote URL 설정 중...
git remote set-url origin https://!TOKEN!@github.com/khanyong/kyyquant-ai-solution.git

echo.
echo 브랜치 푸시 중...
git push -u origin feature/supabase-n8n-integration

if !errorlevel! equ 0 (
    echo.
    echo 성공! 브랜치가 GitHub에 푸시되었습니다.
    echo.
    echo 보안을 위해 remote URL을 원래대로 복원합니다...
    git remote set-url origin https://github.com/khanyong/kyyquant-ai-solution.git
) else (
    echo.
    echo 푸시 실패. Token을 확인해주세요.
    git remote set-url origin https://github.com/khanyong/kyyquant-ai-solution.git
)

endlocal