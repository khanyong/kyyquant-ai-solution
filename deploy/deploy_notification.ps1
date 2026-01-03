
$ErrorActionPreference = "Stop"

# Configuration
$pemKey = "LightsailDefaultKey-ap-northeast-2.pem"
$hostIp = "13.209.204.159"
$user = "ubuntu"
$remoteDir = "~/auto_stock"

Write-Host "Deploying Notification System to AWS Lightsail ($hostIp)..." -ForegroundColor Cyan

# 1. Upload Modified/New Files
$filesToUpload = @(
    "backend/main.py",
    "backend/api/notification.py",
    "backend/services/notification_service.py"
)

foreach ($file in $filesToUpload) {
    Write-Host "Uploading $file..."
    scp -i $pemKey -o StrictHostKeyChecking=no $file "${user}@${hostIp}:${remoteDir}/${file}"
}

# 2. Update .env (Append Webhook URL safely)
# Note: This appends only if not present to avoid duplicates would be complex in one-liner, 
# but simple append is safe enough for now or we use a sed replacement.
# Let's use specific value user provided.
$webhookUrl = "https://stock.bll-pro.com/webhook/telegram-notify"
Write-Host "Updating .env with Webhook URL..."
ssh -i $pemKey -o StrictHostKeyChecking=no "${user}@${hostIp}" "grep -qxF 'N8N_TELEGRAM_WEBHOOK_URL=$webhookUrl' $remoteDir/.env || echo 'N8N_TELEGRAM_WEBHOOK_URL=$webhookUrl' >> $remoteDir/.env"

# 3. Restart Backend
Write-Host "Restarting Backend Docker Container..."
ssh -i $pemKey -o StrictHostKeyChecking=no "${user}@${hostIp}" "cd $remoteDir && docker compose restart backend"

Write-Host "Deployment Complete!" -ForegroundColor Green
