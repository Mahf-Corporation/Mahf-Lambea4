@echo off
REM Setup script for Mahf CPU Driver Inno Setup

setlocal enabledelayedexpansion

echo.
echo ===================================
echo Mahf CPU Driver Setup Builder
echo Version 3.0.2
echo ===================================
echo.

REM Check Inno Setup
echo [*] Checking Inno Setup installation...
where ISCC.exe >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Inno Setup not found!
    echo [INFO] Please install Inno Setup from: https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo [OK] Inno Setup found

REM Build the application first
echo.
echo [*] Building application...
call build.bat
if errorlevel 1 (
    echo.
    echo [ERROR] Application build failed!
    pause
    exit /b 1
)

REM Build setup
echo.
echo [*] Building installer...
ISCC.exe setup.iss
if errorlevel 1 (
    echo.
    echo [ERROR] Installer build failed!
    pause
    exit /b 1
)

echo.
echo ===================================
echo Installer Created Successfully!
echo ===================================
echo.
pause
