#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Creates MahfControlPanel.exe by copying a working system executable
#>

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Mahf Control Panel Executable Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Create Bin directory if needed
if (-not (Test-Path "Bin")) {
    New-Item -ItemType Directory -Path "Bin" -Force | Out-Null
    Write-Host "[OK] Bin directory created" -ForegroundColor Green
}

# Find and copy a working exe
$sourceExe = "C:\Windows\System32\notepad.exe"

if (Test-Path $sourceExe) {
    Write-Host "[*] Copying Notepad.exe as template..." -ForegroundColor Yellow
    Copy-Item $sourceExe "Bin\MahfControlPanel.exe" -Force
    
    $size = (Get-Item "Bin\MahfControlPanel.exe").Length
    Write-Host "[OK] Created: Bin\MahfControlPanel.exe ($($size) bytes)" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Note: This is a placeholder executable for testing." -ForegroundColor Cyan
    Write-Host "To build the real WPF application, use: dotnet build" -ForegroundColor Cyan
    
} else {
    Write-Host "[ERROR] Could not find notepad.exe" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Done!" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
