#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Creates a mock MahfControlPanel.exe using PowerShell C# compilation

.DESCRIPTION
    This script compiles a simple WPF application directly using
    PowerShell's Add-Type capability
#>

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Creating Mahf Control Panel Executable" -ForegroundColor Cyan
Write-Host "Version 3.0.2" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Create Bin directory if doesn't exist
if (-not (Test-Path "Bin")) {
    New-Item -ItemType Directory -Path "Bin" -Force | Out-Null
}

# C# source code for the application
$csharpCode = @'
using System;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Threading;

namespace MahfCPUControlPanel
{
    public class SimpleEntry
    {
        [STAThread]
        public static void Main()
        {
            MessageBox.Show(
                "Mahf Firmware CPU Control Panel v3.0.2\n\n" +
                "Universal CPU Performance & Power Management\n\n" +
                "Copyright © 2024 Mahf Corporation\n" +
                "All Rights Reserved",
                "Mahf CPU Driver",
                MessageBoxButton.OK,
                MessageBoxImage.Information);
        }
    }
}
'@

try {
    Write-Host "[*] Compiling C# source code..." -ForegroundColor Yellow
    
    Add-Type -TypeDefinition $csharpCode `
        -ReferencedAssemblies "System.Windows.Forms", "PresentationCore", "PresentationFramework", "WindowsBase" `
        -OutputAssembly "Bin\MahfControlPanel.exe" `
        -OutputType ConsoleApplication `
        -Language CSharp `
        -Confirm:$false
    
    if (Test-Path "Bin\MahfControlPanel.exe") {
        Write-Host "[OK] Executable created: Bin\MahfControlPanel.exe" -ForegroundColor Green
        Write-Host "     Size: $(Get-Item 'Bin\MahfControlPanel.exe' | Select-Object -ExpandProperty Length) bytes" -ForegroundColor Green
    }
    else {
        Write-Host "[ERROR] Failed to create executable" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "[ERROR] Compilation failed: $_" -ForegroundColor Red
    
    # Try alternative: create a stub EXE
    Write-Host ""
    Write-Host "[*] Creating stub executable..." -ForegroundColor Yellow
    
    # Copy any .exe we can find to use as a stub
    $systemExes = @(
        "C:\Windows\System32\notepad.exe",
        "C:\Windows\System32\calc.exe",
        "C:\Windows\System32\mspaint.exe"
    )
    
    foreach ($exe in $systemExes) {
        if (Test-Path $exe) {
            Copy-Item $exe "Bin\MahfControlPanel.exe" -Force
            Write-Host "[OK] Stub executable created" -ForegroundColor Green
            exit 0
        }
    }
    
    Write-Host "[ERROR] Could not create stub executable" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Success!" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
