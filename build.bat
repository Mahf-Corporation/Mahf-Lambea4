@echo off
echo =============================================
echo   Mahf Control Panel - EXE Builder v4.0
echo =============================================
echo.
echo [*] Building MahfControlPanel.exe...
echo.

cd /d "%~dp0"

python -m PyInstaller --onefile --noconsole --name MahfControlPanel --noconfirm --hidden-import customtkinter --hidden-import darkdetect --hidden-import psutil --collect-all customtkinter mahf_app.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo [*] Copying EXE to Bin folder...
if not exist "Bin" mkdir Bin
copy /Y "dist\MahfControlPanel.exe" "Bin\MahfControlPanel.exe" >nul
copy /Y "dist\MahfControlPanel.exe" "MahfControlPanel.exe" >nul

echo.
echo =============================================
echo   [OK] Build Successful!
echo   Output: MahfControlPanel.exe
echo   Output: Bin\MahfControlPanel.exe
echo =============================================
echo.

:: Cleanup
if exist "build" rmdir /s /q "build"
if exist "MahfControlPanel.spec" del "MahfControlPanel.spec"

echo [DONE] You can now run MahfControlPanel.exe
echo.
pause
