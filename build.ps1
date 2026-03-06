#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Builds the Mahf CPU Driver project with all dependencies

.DESCRIPTION
    This script handles:
    - Checking for .NET SDK
    - Installing .NET SDK if needed
    - Building the WPF application
    - Creating installer files

.PARAMETER InstallDotNet
    Automatically install .NET SDK if not found
#>

param(
    [switch]$InstallDotNet,
    [switch]$SkipBuild,
    [switch]$SkipSetup
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Mahf Firmware CPU Driver Build" -ForegroundColor Cyan
Write-Host "Version 3.0.2" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check for .NET SDK
Write-Host "[*] Checking for .NET SDK..." -ForegroundColor Yellow
$dotnetPath = Get-Command dotnet -ErrorAction SilentlyContinue

if (-not $dotnetPath) {
    Write-Host "[!] .NET SDK not found" -ForegroundColor Red
    
    if ($InstallDotNet -or (Read-Host "Install .NET SDK? (Y/N)").ToUpper() -eq "Y") {
        Write-Host "[*] Downloading .NET SDK 9.0..." -ForegroundColor Yellow
        
        $dotnetInstaller = "$env:TEMP\dotnet-sdk.exe"
        $downloadUrl = "https://aka.ms/dotnet/9.0.0/windowsx64"
        
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -Uri $downloadUrl -OutFile $dotnetInstaller -UseBasicParsing
            
            Write-Host "[*] Installing .NET SDK..." -ForegroundColor Yellow
            & $dotnetInstaller /install /quiet /norestart
            
            Write-Host "[OK] .NET SDK installed" -ForegroundColor Green
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        }
        catch {
            Write-Host "[ERROR] Failed to download/install .NET SDK: $_" -ForegroundColor Red
            Write-Host "[INFO] Please download from: https://aka.ms/dotnet/download" -ForegroundColor Yellow
            exit 1
        }
    }
    else {
        Write-Host "[ERROR] .NET SDK is required to build this project" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "[OK] .NET SDK found at: $($dotnetPath.Source)" -ForegroundColor Green
    $version = dotnet --version 2>$null
    Write-Host "     Version: $version" -ForegroundColor Green
}

# Create output directories
Write-Host ""
Write-Host "[*] Creating directories..." -ForegroundColor Yellow
$dirs = @("Output", "Bin", "MahfControlPanel\bin", "MahfControlPanel\obj")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "     Created: $dir" -ForegroundColor Green
    }
}

# Clean previous builds
Write-Host ""
Write-Host "[*] Cleaning previous builds..." -ForegroundColor Yellow
$cleanDirs = @("MahfControlPanel\bin", "MahfControlPanel\obj")
foreach ($dir in $cleanDirs) {
    if (Test-Path $dir) {
        Remove-Item -Path $dir -Recurse -Force -ErrorAction SilentlyContinue
    }
}
Write-Host "[OK] Cleanup complete" -ForegroundColor Green

# Build WPF Application
if (-not $SkipBuild) {
    Write-Host ""
    Write-Host "[*] Building WPF Application..." -ForegroundColor Yellow
    
    try {
        Push-Location MahfControlPanel
        
        Write-Host "     Restoring dependencies..." -ForegroundColor Yellow
        dotnet restore *>$null
        
        Write-Host "     Compiling..." -ForegroundColor Yellow
        dotnet build -c Release --no-restore
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] WPF Application built successfully" -ForegroundColor Green
        }
        else {
            Write-Host "[ERROR] Build failed" -ForegroundColor Red
            Pop-Location
            exit 1
        }
        
        # Find compiled executable
        $exePaths = @(
            "bin\Release\net9.0-windows\MahfControlPanel.exe",
            "bin\Release\net9.0\MahfControlPanel.exe",
            "bin\Release\net8.0-windows\MahfControlPanel.exe"
        )
        
        $exePath = $exePaths | Where-Object { Test-Path $_ } | Select-Object -First 1
        
        if ($exePath) {
            New-Item -ItemType Directory -Path "..\Bin" -Force | Out-Null
            Copy-Item -Path $exePath -Destination "..\Bin\MahfControlPanel.exe" -Force
            Write-Host "[OK] Executable copied to Bin\MahfControlPanel.exe" -ForegroundColor Green
        }
        else {
            Write-Host "[ERROR] Compiled executable not found" -ForegroundColor Red
            Pop-Location
            exit 1
        }
        
        Pop-Location
    }
    catch {
        Write-Host "[ERROR] Build error: $_" -ForegroundColor Red
        Pop-Location
        exit 1
    }
}

# Create driver placeholder files
Write-Host ""
Write-Host "[*] Creating driver files..." -ForegroundColor Yellow

if (-not (Test-Path "Driver")) {
    New-Item -ItemType Directory -Path "Driver" -Force | Out-Null
}

# Create INF file
$infContent = @"
[Version]
Signature="`$CHICAGO`$"
Class=System
ClassGuid={4D36E97D-E325-11CE-BFC1-08002BE10318}
Provider=%MAHF%
DriverVer=01/01/2024,3.0.2.0

[Manufacturer]
%MAHF%=MAHF,NT.10.0

[MAHF.NT.10.0]
%MAHF_DESC%=mahf_core,ACPI\MAHF_CPU

[mahf_core.NT]
Copy=mahf_core.sys.files

[mahf_core.sys.files]
mahf_core.sys

[mahf_core.NT.HW]
AddReg=mahf_core.HW.AddReg

[mahf_core.HW.AddReg]
HKR,,Class,0x00000070,"System"
HKR,,ClassGuid,0x00000070,"{4D36E97D-E325-11CE-BFC1-08002BE10318}"

[SourceDisksNames]
1="Mahf CPU Driver",,

[SourceDisksFiles]
mahf_core.sys=1

[DestinationDirs]
mahf_core.sys.files=12

[Strings]
MAHF="Mahf Corporation"
MAHF_DESC="Mahf CPU Driver"
"@

$infContent | Set-Content -Path "Driver\mahf_cpu.inf" -Force
Write-Host "     Created: Driver\mahf_cpu.inf" -ForegroundColor Green

# Build installer if Inno Setup is available
if (-not $SkipSetup) {
    Write-Host ""
    Write-Host "[*] Checking for Inno Setup..." -ForegroundColor Yellow
    
    $iscc = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    
    if ($iscc) {
        Write-Host "[OK] Inno Setup found" -ForegroundColor Green
        Write-Host "[*] Building installer..." -ForegroundColor Yellow
        
        try {
            & ISCC.exe setup.iss
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[OK] Installer created successfully" -ForegroundColor Green
                Write-Host "     Setup file: Output\MahfCPUSetup_3.0.2.exe" -ForegroundColor Green
            }
            else {
                Write-Host "[!] Installer build encountered warnings" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "[ERROR] Installer build failed: $_" -ForegroundColor Red
        }
    }
    else {
        Write-Host "[!] Inno Setup not found (optional)" -ForegroundColor Yellow
        Write-Host "    Install from: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Build Complete!" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output Files:" -ForegroundColor Green
Write-Host "  Executable: Bin\MahfControlPanel.exe" -ForegroundColor Green
if (Test-Path "Output\MahfCPUSetup_3.0.2.exe") {
    Write-Host "  Installer:  Output\MahfCPUSetup_3.0.2.exe" -ForegroundColor Green
}
Write-Host ""
