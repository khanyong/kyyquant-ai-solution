# PowerShell script to force OpenAPI installation with elevated privileges
# Run this script as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OpenAPI+ Force Installation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Write-Host "This script requires Administrator privileges!" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Step 1: Check and install prerequisites
Write-Host "Step 1: Checking Prerequisites..." -ForegroundColor Yellow

# Check .NET Framework
$dotNetVersion = Get-ItemProperty "HKLM:SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full\" -Name Release -ErrorAction SilentlyContinue
if ($dotNetVersion -eq $null -or $dotNetVersion.Release -lt 461808) {
    Write-Host "[WARNING] .NET Framework 4.7.2 or higher required" -ForegroundColor Red
    Write-Host "Download from: https://dotnet.microsoft.com/download/dotnet-framework" -ForegroundColor Yellow
}
else {
    Write-Host "[OK] .NET Framework version adequate" -ForegroundColor Green
}

# Step 2: Clean previous installation
Write-Host ""
Write-Host "Step 2: Cleaning previous installation..." -ForegroundColor Yellow

# Unregister OCX files
$ocxFiles = @("khopenapi.ocx", "khoapicomm.ocx")
foreach ($ocx in $ocxFiles) {
    $ocxPath = "C:\OpenAPI\$ocx"
    if (Test-Path $ocxPath) {
        Write-Host "Unregistering $ocx..." -ForegroundColor Gray
        Start-Process regsvr32.exe -ArgumentList "/u /s `"$ocxPath`"" -Wait -NoNewWindow
    }
}

# Remove registry entries
Write-Host "Removing registry entries..." -ForegroundColor Gray
Remove-Item "HKLM:\SOFTWARE\WOW6432Node\KHOpenAPI" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "HKLM:\SOFTWARE\KHOpenAPI" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "HKCU:\Software\KHOpenAPI" -Recurse -Force -ErrorAction SilentlyContinue

# Step 3: Create directory with proper permissions
Write-Host ""
Write-Host "Step 3: Setting up directory..." -ForegroundColor Yellow

if (-not (Test-Path "C:\OpenAPI")) {
    New-Item -ItemType Directory -Path "C:\OpenAPI" -Force | Out-Null
}

# Set full permissions
$acl = Get-Acl "C:\OpenAPI"
$permission = "Everyone","FullControl","ContainerInherit,ObjectInherit","None","Allow"
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule $permission
$acl.SetAccessRule($accessRule)
Set-Acl "C:\OpenAPI" $acl
Write-Host "[OK] Directory permissions set" -ForegroundColor Green

# Step 4: Add Windows Defender exclusions
Write-Host ""
Write-Host "Step 4: Adding Windows Defender exclusions..." -ForegroundColor Yellow
try {
    Add-MpPreference -ExclusionPath "C:\OpenAPI" -ErrorAction SilentlyContinue
    Add-MpPreference -ExclusionProcess "C:\OpenAPI\*.exe" -ErrorAction SilentlyContinue
    Write-Host "[OK] Windows Defender exclusions added" -ForegroundColor Green
}
catch {
    Write-Host "[WARNING] Could not add Windows Defender exclusions" -ForegroundColor Yellow
}

# Step 5: Download OpenAPI+ if not exists
Write-Host ""
Write-Host "Step 5: OpenAPI+ Installation..." -ForegroundColor Yellow

$installerPath = "$env:TEMP\OpenAPISetup.exe"
$downloadUrl = "https://download.kiwoom.com/web/openapi/OpenAPISetup.exe"

if (-not (Test-Path $installerPath)) {
    Write-Host "Downloading OpenAPI+ installer..." -ForegroundColor Gray
    try {
        # Disable SSL certificate validation temporarily
        [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
        
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($downloadUrl, $installerPath)
        Write-Host "[OK] Installer downloaded" -ForegroundColor Green
    }
    catch {
        Write-Host "[ERROR] Failed to download installer" -ForegroundColor Red
        Write-Host "Please download manually from: $downloadUrl" -ForegroundColor Yellow
        Write-Host "Save as: $installerPath" -ForegroundColor Yellow
        Read-Host "Press Enter after downloading"
    }
}

if (Test-Path $installerPath) {
    Write-Host "Running OpenAPI+ installer..." -ForegroundColor Gray
    Write-Host "IMPORTANT: When installer opens, just click through with default settings" -ForegroundColor Yellow
    Start-Process $installerPath -Wait
    Write-Host "[OK] Installation completed" -ForegroundColor Green
}

# Step 6: Manual OCX registration
Write-Host ""
Write-Host "Step 6: Registering OCX components..." -ForegroundColor Yellow

Set-Location "C:\OpenAPI"
$ocxFiles = Get-ChildItem -Path "C:\OpenAPI" -Filter "*.ocx"

foreach ($ocx in $ocxFiles) {
    Write-Host "Registering $($ocx.Name)..." -ForegroundColor Gray
    $result = Start-Process regsvr32.exe -ArgumentList "/s `"$($ocx.FullName)`"" -Wait -PassThru -NoNewWindow
    if ($result.ExitCode -eq 0) {
        Write-Host "[OK] $($ocx.Name) registered successfully" -ForegroundColor Green
    }
    else {
        Write-Host "[ERROR] Failed to register $($ocx.Name)" -ForegroundColor Red
    }
}

# Step 7: Verify installation
Write-Host ""
Write-Host "Step 7: Verifying installation..." -ForegroundColor Yellow

$verifyItems = @{
    "C:\OpenAPI\khopenapi.ocx" = "Main OCX file"
    "C:\OpenAPI\khoapicomm.ocx" = "Communication OCX file"
    "C:\OpenAPI\bin\khoapicomm.exe" = "Communication executable"
}

$allGood = $true
foreach ($item in $verifyItems.GetEnumerator()) {
    if (Test-Path $item.Key) {
        Write-Host "[OK] $($item.Value) found" -ForegroundColor Green
    }
    else {
        Write-Host "[ERROR] $($item.Value) missing: $($item.Key)" -ForegroundColor Red
        $allGood = $false
    }
}

# Check registry
$regKey = Get-ItemProperty "HKLM:\SOFTWARE\WOW6432Node\KHOpenAPI" -ErrorAction SilentlyContinue
if ($regKey) {
    Write-Host "[OK] Registry entries found" -ForegroundColor Green
}
else {
    Write-Host "[WARNING] Registry entries not found" -ForegroundColor Yellow
    $allGood = $false
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "SUCCESS: OpenAPI+ installation verified!" -ForegroundColor Green
    Write-Host "You can now proceed with KOA Studio installation." -ForegroundColor Green
}
else {
    Write-Host "WARNING: Some components missing or not registered." -ForegroundColor Yellow
    Write-Host "Try running this script again or contact Kiwoom support." -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"