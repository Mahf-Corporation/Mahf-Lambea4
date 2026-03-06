#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Mahf Firmware CPU Driver - PowerShell Installer

.DESCRIPTION
    This script installs the Mahf CPU Control Panel and optionally the driver

.PARAMETER InstallDir
    Installation directory (default: C:\Program Files\Mahf\CPU Driver)

.PARAMETER CreateStartMenu
    Create Windows Start Menu shortcuts

.PARAMETER CreateDesktopShortcut
    Create desktop shortcut
#>

param(
    [string]$InstallDir = "C:\Program Files\Mahf\CPU Driver",
    [switch]$CreateStartMenu = $true,
    [switch]$CreateDesktopShortcut = $true,
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"
$Version = "3.0.2"

# Check for admin rights
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]"Administrator")
if (-not $isAdmin) {
    Write-Host "This installer requires administrator rights!" -ForegroundColor Red
    Write-Host "Please run: powershell -RunAs Administrator" -ForegroundColor Yellow
    exit 1
}

if ($Uninstall) {
    Write-Host ""
    Write-Host "Uninstalling Mahf CPU Driver..." -ForegroundColor Yellow
    
    if (Test-Path $InstallDir) {
        Remove-Item -Path $InstallDir -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "[OK] Installation directory removed" -ForegroundColor Green
    }
    
    # Remove Start Menu shortcuts
    $startMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Mahf CPU Driver"
    if (Test-Path $startMenuPath) {
        Remove-Item -Path $startMenuPath -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "[OK] Start Menu shortcuts removed" -ForegroundColor Green
    }
    
    # Remove Desktop shortcut
    $desktopPath = "$env:USERPROFILE\Desktop\Mahf CPU Driver.lnk"
    if (Test-Path $desktopPath) {
        Remove-Item -Path $desktopPath -Force -ErrorAction SilentlyContinue
        Write-Host "[OK] Desktop shortcut removed" -ForegroundColor Green
    }
    
    # Remove registry entries
    Remove-Item -Path "HKLM:\SOFTWARE\Mahf\CPU" -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-Host "[OK] Uninstall complete" -ForegroundColor Green
    exit 0
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Mahf Firmware CPU Driver v$Version" -ForegroundColor Cyan
Write-Host "Installation Wizard" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host "[*] Installation Directory: $InstallDir" -ForegroundColor Yellow

# Create installation directory
Write-Host "[*] Creating installation directory..." -ForegroundColor Yellow
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    Write-Host "[OK] Directory created" -ForegroundColor Green
}

# Copy executable
Write-Host "[*] Copying application files..." -ForegroundColor Yellow
$exePath = Join-Path $scriptDir "Bin\MahfControlPanel.exe"

if (Test-Path $exePath) {
    Copy-Item -Path $exePath -Destination "$InstallDir\MahfControlPanel.exe" -Force
    Write-Host "[OK] Application copied" -ForegroundColor Green
} else {
    Write-Host "[ERROR] MahfControlPanel.exe not found!" -ForegroundColor Red
    exit 1
}

# Copy README
$readmePath = Join-Path $scriptDir "README.md"
if (Test-Path $readmePath) {
    Copy-Item -Path $readmePath -Destination "$InstallDir\README.md" -Force
}

# Copy LICENSE
$licensePath = Join-Path $scriptDir "LICENSE.txt"
if (Test-Path $licensePath) {
    Copy-Item -Path $licensePath -Destination "$InstallDir\LICENSE.txt" -Force
}

# Create Start Menu shortcuts
if ($CreateStartMenu) {
    Write-Host "[*] Creating Start Menu shortcuts..." -ForegroundColor Yellow
    
    $startMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Mahf CPU Driver"
    if (-not (Test-Path $startMenuPath)) {
        New-Item -ItemType Directory -Path $startMenuPath -Force | Out-Null
    }
    
    # Application shortcut
    $WshShell = New-Object -ComObject WScript.Shell
    $shortcut = $WshShell.CreateShortcut("$startMenuPath\Mahf CPU Driver.lnk")
    $shortcut.TargetPath = "$InstallDir\MahfControlPanel.exe"
    $shortcut.WorkingDirectory = $InstallDir
    $shortcut.Description = "Mahf Firmware CPU Control Panel"
    $shortcut.Save()
    
    # Uninstall shortcut
    $uninstallShortcut = $WshShell.CreateShortcut("$startMenuPath\Uninstall.lnk")
    $uninstallShortcut.TargetPath = "powershell.exe"
    $uninstallShortcut.Arguments = "-NoProfile -Command & {$($MyInvocation.MyCommand.Definition) -Uninstall}"
    $uninstallShortcut.Description = "Uninstall Mahf CPU Driver"
    $uninstallShortcut.Save()
    
    Write-Host "[OK] Shortcuts created" -ForegroundColor Green
}

# Create Desktop shortcut
if ($CreateDesktopShortcut) {
    Write-Host "[*] Creating Desktop shortcut..." -ForegroundColor Yellow
    
    $WshShell = New-Object -ComObject WScript.Shell
    $desktopPath = "$env:USERPROFILE\Desktop\Mahf CPU Driver.lnk"
    $shortcut = $WshShell.CreateShortcut($desktopPath)
    $shortcut.TargetPath = "$InstallDir\MahfControlPanel.exe"
    $shortcut.WorkingDirectory = $InstallDir
    $shortcut.Description = "Mahf Firmware CPU Control Panel"
    $shortcut.Save()
    
    Write-Host "[OK] Desktop shortcut created" -ForegroundColor Green
}

# Create registry entries
Write-Host "[*] Creating registry entries..." -ForegroundColor Yellow
$regPath = "HKLM:\SOFTWARE\Mahf\CPU"
if (-not (Test-Path $regPath)) {
    New-Item -Path $regPath -Force | Out-Null
}
New-ItemProperty -Path $regPath -Name "Version" -Value $Version -PropertyType String -Force | Out-Null
New-ItemProperty -Path $regPath -Name "InstallPath" -Value $InstallDir -PropertyType String -Force | Out-Null
Write-Host "[OK] Registry entries created" -ForegroundColor Green

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Installed to: $InstallDir" -ForegroundColor Green
Write-Host ""

# Ask to launch application
$response = Read-Host "Launch Mahf CPU Driver now? (Y/N)"
if ($response -eq "Y" -or $response -eq "y") {
    & "$InstallDir\MahfControlPanel.exe"
}
