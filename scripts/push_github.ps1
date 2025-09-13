# GitHub Push Script
Write-Host "GitHub Token을 입력하세요 (ghp_로 시작):" -ForegroundColor Yellow
$token = Read-Host -AsSecureString

# SecureString을 일반 문자열로 변환
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($token)
$tokenPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Remote URL 설정
$remoteUrl = "https://$tokenPlain@github.com/khanyong/kyyquant-ai-solution.git"
git remote set-url origin $remoteUrl

Write-Host "`n브랜치를 푸시합니다..." -ForegroundColor Green
git push -u origin feature/supabase-n8n-integration

# 보안을 위해 remote URL 복원
Write-Host "`n보안을 위해 remote URL을 복원합니다..." -ForegroundColor Yellow
git remote set-url origin https://github.com/khanyong/kyyquant-ai-solution.git

Write-Host "`n완료!" -ForegroundColor Green