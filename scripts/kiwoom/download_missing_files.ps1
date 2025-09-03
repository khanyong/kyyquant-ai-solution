# PowerShell script to download missing OpenAPI files
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Downloading Missing OpenAPI Files" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Write-Host "[ERROR] Administrator privileges required!" -ForegroundColor Red
    Write-Host "Run PowerShell as Administrator" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Set location
Set-Location "C:\OpenAPI"

# Download OpenAPI installer
$installerUrl = "https://download.kiwoom.com/web/openapi/OpenAPISetup.exe"
$installerPath = "$env:TEMP\OpenAPISetup.exe"

Write-Host "Downloading OpenAPI+ installer..." -ForegroundColor Yellow
try {
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "[OK] Installer downloaded" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Failed to download. Please download manually from:" -ForegroundColor Red
    Write-Host $installerUrl -ForegroundColor Yellow
    Read-Host "Press Enter after downloading"
}

if (Test-Path $installerPath) {
    Write-Host ""
    Write-Host "Extracting files from installer..." -ForegroundColor Yellow
    
    # Create temp extraction directory
    $extractPath = "$env:TEMP\OpenAPIExtract"
    if (Test-Path $extractPath) {
        Remove-Item $extractPath -Recurse -Force
    }
    New-Item -ItemType Directory -Path $extractPath -Force | Out-Null
    
    # Try to extract using 7-Zip if available
    $sevenZip = "C:\Program Files\7-Zip\7z.exe"
    if (Test-Path $sevenZip) {
        & $sevenZip x $installerPath -o"$extractPath" -y | Out-Null
        Write-Host "[OK] Files extracted using 7-Zip" -ForegroundColor Green
    }
    else {
        Write-Host "Running installer in silent mode..." -ForegroundColor Yellow
        Start-Process $installerPath -ArgumentList "/S" -Wait
        Write-Host "[OK] Installation completed" -ForegroundColor Green
    }
}

# Register OCX files using 32-bit regsvr32
Write-Host ""
Write-Host "Registering OCX components (32-bit)..." -ForegroundColor Yellow

$ocxFiles = @("khopenapi.ocx", "khoapicomm.ocx")
foreach ($ocx in $ocxFiles) {
    $ocxPath = "C:\OpenAPI\$ocx"
    if (Test-Path $ocxPath) {
        Write-Host "Registering $ocx..." -ForegroundColor Gray
        $result = Start-Process "C:\Windows\SysWOW64\regsvr32.exe" -ArgumentList "/s `"$ocxPath`"" -Wait -PassThru -NoNewWindow
        if ($result.ExitCode -eq 0) {
            Write-Host "[OK] $ocx registered" -ForegroundColor Green
        }
        else {
            Write-Host "[ERROR] Failed to register $ocx" -ForegroundColor Red
        }
    }
    else {
        Write-Host "[WARNING] $ocx not found" -ForegroundColor Yellow
    }
}

# Create registry entries
Write-Host ""
Write-Host "Creating registry entries..." -ForegroundColor Yellow
New-Item -Path "HKLM:\SOFTWARE\WOW6432Node\KHOpenAPI" -Force | Out-Null
New-Item -Path "HKLM:\SOFTWARE\WOW6432Node\KHOpenAPI\Config" -Force | Out-Null
Set-ItemProperty -Path "HKLM:\SOFTWARE\WOW6432Node\KHOpenAPI\Config" -Name "InstallPath" -Value "C:\OpenAPI"
Set-ItemProperty -Path "HKLM:\SOFTWARE\WOW6432Node\KHOpenAPI\Config" -Name "Version" -Value "1.0.0.0"
Write-Host "[OK] Registry entries created" -ForegroundColor Green

# Enable UAC if disabled
$uacStatus = Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA"
if ($uacStatus.EnableLUA -eq 0) {
    Write-Host ""
    Write-Host "[WARNING] UAC is disabled. Enabling UAC..." -ForegroundColor Yellow
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "EnableLUA" -Value 1
    Write-Host "[OK] UAC enabled - RESTART REQUIRED" -ForegroundColor Green
    $restartNeeded = $true
}

# Final verification
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verification:" -ForegroundColor Cyan

$allGood = $true
if (Test-Path "C:\OpenAPI\khopenapi.ocx") {
    Write-Host "[OK] khopenapi.ocx exists" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] khopenapi.ocx missing" -ForegroundColor Red
    $allGood = $false
}

if (Test-Path "C:\OpenAPI\khoapicomm.ocx") {
    Write-Host "[OK] khoapicomm.ocx exists" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] khoapicomm.ocx missing" -ForegroundColor Red
    $allGood = $false
}

$regKey = Get-ItemProperty "HKLM:\SOFTWARE\WOW6432Node\KHOpenAPI\Config" -ErrorAction SilentlyContinue
if ($regKey) {
    Write-Host "[OK] Registry entries found" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] Registry entries missing" -ForegroundColor Red
    $allGood = $false
}

Write-Host "========================================" -ForegroundColor Cyan

if ($restartNeeded) {
    Write-Host ""
    Write-Host "IMPORTANT: Restart required!" -ForegroundColor Yellow
    Write-Host "Restart now? (Y/N)" -ForegroundColor Yellow
    $restart = Read-Host
    if ($restart -eq "Y") {
        Restart-Computer -Force
    }
}
elseif ($allGood) {
    Write-Host "SUCCESS: OpenAPI+ is ready!" -ForegroundColor Green
    Write-Host "You can now install KOA Studio." -ForegroundColor Green
}
else {
    Write-Host "Some components are still missing." -ForegroundColor Yellow
    Write-Host "Try running the installer manually." -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"