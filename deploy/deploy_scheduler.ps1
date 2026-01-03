
# deploy/deploy_scheduler.ps1
# Deploy Scheduler & Strategy Service to AWS Lightsail

$pemKey = "LightsailDefaultKey-ap-northeast-2.pem"
$hostIp = "13.209.204.159"
$user = "ubuntu"
$remoteDir = "/home/ubuntu/auto_stock"

Write-Host "Starting Deployment: Scheduler & Strategy Service..."

# 1. Upload Files
$filesToUpload = @(
    "backend/main.py",
    "backend/services/scheduler_service.py",
    "backend/services/strategy_service.py"
)

foreach ($file in $filesToUpload) {
    Write-Host "Uploading $file..."
    # Create directory if strictly needed (services/ might exist from notification_service, but good to ensure)
    # Actually services/ exists.
    scp -i $pemKey -o StrictHostKeyChecking=no $file "${user}@${hostIp}:${remoteDir}/${file}"
}

# 2. Restart Backend
Write-Host "Restarting Backend Docker Container..."
ssh -i $pemKey -o StrictHostKeyChecking=no "${user}@${hostIp}" "cd $remoteDir && docker compose restart backend"

Write-Host "✅ Deployment Complete! Scheduler should be running."
