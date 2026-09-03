# Unfolder - Windows PowerShell Installer
# Run as: powershell -ExecutionPolicy Bypass -File install_windows.ps1
#
# Installs Unfolder's GUI to %LOCALAPPDATA%\Unfolder and creates a
# desktop shortcut that launches it silently (no console, no PowerShell)
# so end users can just double-click and go.

param(
    [string]$InstallDir = "$env:LOCALAPPDATA\Unfolder",
    [switch]$CreateStartMenuShortcut,
    [switch]$InstallOptionalFormats   # adds RAR / 7Z support (py7zr, rarfile)
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host " Unfolder - Windows Installer" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# [1/6] Check Python
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python not found. Please install Python 3.7+ first (python.org)." -ForegroundColor Red
    Write-Host "  Be sure to check 'Add python.exe to PATH' during install." -ForegroundColor Red
    exit 1
}

# Confirm pythonw.exe exists (needed for a console-free launch)
$pythonwCheck = Get-Command pythonw.exe -ErrorAction SilentlyContinue
if (-not $pythonwCheck) {
    Write-Host "  WARNING: pythonw.exe not found on PATH. Shortcut will fall back to python.exe" -ForegroundColor Yellow
    Write-Host "  (a console window may briefly flash when launching)." -ForegroundColor Yellow
}

# [2/6] Create install directory
Write-Host "[2/6] Creating installation directory..." -ForegroundColor Yellow
if (!(Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}
Write-Host "  Location: $InstallDir" -ForegroundColor Green

# [3/6] Copy files
Write-Host "[3/6] Copying Unfolder files..." -ForegroundColor Yellow
$sourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$filesToCopy = @("unfolder.py", "unfolder_gui.py", "requirements.txt")
foreach ($file in $filesToCopy) {
    $sourcePath = Join-Path $sourceDir $file
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath $InstallDir -Force
        Write-Host "  Copied: $file" -ForegroundColor Green
    } else {
        Write-Host "  Skipped (not found next to installer): $file" -ForegroundColor DarkYellow
    }
}

# Copy icon if you add one later (icons\Unfolder.ico)
$iconSource = Join-Path $sourceDir "icons\Unfolder.ico"
$iconDest = Join-Path $InstallDir "Unfolder.ico"
$haveIcon = $false
if (Test-Path $iconSource) {
    Copy-Item $iconSource $iconDest -Force
    $haveIcon = $true
    Write-Host "  Copied: Unfolder.ico" -ForegroundColor Green
}

# [4/6] Optional dependencies (RAR / 7Z support)
Write-Host "[4/6] Optional format support..." -ForegroundColor Yellow
if ($InstallOptionalFormats) {
    try {
        python -m pip install py7zr rarfile --quiet
        Write-Host "  Installed py7zr + rarfile (RAR/7Z support enabled)" -ForegroundColor Green
    } catch {
        Write-Host "  Could not install optional packages - ZIP/TAR/GZ/BZ2 still work fine." -ForegroundColor DarkYellow
    }
} else {
    Write-Host "  Skipped (run with -InstallOptionalFormats to add RAR/7Z support)" -ForegroundColor DarkYellow
}

# [5/6] Create a hidden-console launcher (.vbs) so double-click never shows a black window
Write-Host "[5/6] Creating launcher..." -ForegroundColor Yellow
$pyw = if ($pythonwCheck) { "pythonw" } else { "python" }
$vbsContent = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "$InstallDir"
WshShell.Run """$pyw"" ""$InstallDir\unfolder_gui.py""", 0, False
"@
$vbsPath = Join-Path $InstallDir "Unfolder.vbs"
Set-Content -Path $vbsPath -Value $vbsContent
Write-Host "  Created: Unfolder.vbs (silent launcher)" -ForegroundColor Green

# [6/6] Create shortcuts
Write-Host "[6/6] Creating shortcuts..." -ForegroundColor Yellow

function New-AppShortcut {
    param($ShortcutPath, $TargetPath, $Arguments, $IconPath, $WorkingDir, $Description)
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $TargetPath
    $Shortcut.Arguments = $Arguments
    $Shortcut.WorkingDirectory = $WorkingDir
    $Shortcut.Description = $Description
    if ($IconPath -and (Test-Path $IconPath)) {
        $Shortcut.IconLocation = $IconPath
    }
    $Shortcut.Save()
}

$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutIcon = if ($haveIcon) { $iconDest } else { "" }

$desktopShortcut = Join-Path $desktopPath "Unfolder.lnk"
New-AppShortcut -ShortcutPath $desktopShortcut `
    -TargetPath "wscript.exe" `
    -Arguments "`"$vbsPath`"" `
    -IconPath $shortcutIcon `
    -WorkingDir $InstallDir `
    -Description "Unfolder - Extract nested archives"
Write-Host "  Created: Unfolder.lnk on Desktop" -ForegroundColor Green

if ($CreateStartMenuShortcut) {
    $startMenuPath = [Environment]::GetFolderPath("StartMenu")
    $programsPath = Join-Path $startMenuPath "Programs\Unfolder"
    if (!(Test-Path $programsPath)) {
        New-Item -ItemType Directory -Path $programsPath -Force | Out-Null
    }
    $smShortcut = Join-Path $programsPath "Unfolder.lnk"
    New-AppShortcut -ShortcutPath $smShortcut `
        -TargetPath "wscript.exe" `
        -Arguments "`"$vbsPath`"" `
        -IconPath $shortcutIcon `
        -WorkingDir $InstallDir `
        -Description "Unfolder - Extract nested archives"
    Write-Host "  Created: Start Menu shortcut" -ForegroundColor Green
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host " Installation Complete!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Double-click 'Unfolder' on your Desktop to open the app." -ForegroundColor Yellow
Write-Host "No PowerShell, no command line - just browse to a folder and click Extract." -ForegroundColor Yellow
Write-Host ""
