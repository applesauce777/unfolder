# Interactive PowerShell script to recursively extract nested zip files
# Requires 7-Zip to be installed
#
# LIMITATIONS:
# - Only supports ZIP format (not RAR, 7Z, TAR, etc.)
# - Requires 7-Zip to be installed separately
# - Windows-only (not cross-platform like Python version)
# - No automatic cleanup of failed extractions
# - No dry-run/preview mode
#
# ADVANTAGES:
# - Better Windows long path support
# - Faster for ZIP-only operations
# - Native Windows integration
# - No Python dependencies

# Path to 7-Zip executable
$7zipPath = "C:\Program Files\7-Zip\7z.exe"

# Check if 7-Zip exists
if (-not (Test-Path $7zipPath)) {
    Write-Host "7-Zip not found at $7zipPath" -ForegroundColor Red
    Write-Host "Please install 7-Zip or update the path in the script" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Recursive Zip Extractor with 7-Zip" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Enable long path support for this session
try {
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -ErrorAction Stop
    Write-Host "Long path support enabled for this session" -ForegroundColor Green
} catch {
    Write-Host "Warning: Could not enable long paths (may need admin rights)" -ForegroundColor Yellow
}
Write-Host ""

# Function to browse for folder
function Get-FolderPath {
    Add-Type -AssemblyName System.Windows.Forms
    $folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
    $folderBrowser.Description = "Select the folder containing your zip files"
    $folderBrowser.RootFolder = "MyComputer"
    
    if ($folderBrowser.ShowDialog() -eq "OK") {
        return $folderBrowser.SelectedPath
    }
    return $null
}

# Get folder from user
Write-Host "Please select the folder containing your zip files..." -ForegroundColor Yellow
$rootFolder = Get-FolderPath

if (-not $rootFolder) {
    Write-Host "No folder selected. Exiting..." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

Write-Host ""
Write-Host "Selected folder: $rootFolder" -ForegroundColor Green
Write-Host ""

# Ask if user wants to delete zip files after extraction
$deleteChoice = Read-Host "Delete zip files after successful extraction? (y/n)"
$deleteZips = $deleteChoice -eq 'y' -or $deleteChoice -eq 'Y'

Write-Host ""

# Global hashset to track already processed files
$script:processedFiles = @{}

# Function to extract ALL zips recursively - turtles all the way down
function Extract-ZipRecursive {
    param (
        [string]$sourcePath,
        [bool]$deleteAfterExtract,
        [int]$depth = 0
    )
    
    $indent = "  " * $depth
    
    # Keep looping until no more NEW zip files are found
    $foundNewZips = $true
    while ($foundNewZips) {
        # Find all zip files recursively in the entire tree
        $allZipFiles = Get-ChildItem -Path $sourcePath -Filter "*.zip" -File -Recurse -ErrorAction SilentlyContinue
        
        # Filter out files we've already processed
        $zipFiles = $allZipFiles | Where-Object { -not $script:processedFiles.ContainsKey($_.FullName) }
        
        if ($zipFiles.Count -eq 0) {
            $foundNewZips = $false
            break
        }
        
        Write-Host "$indent--- Found $($zipFiles.Count) NEW zip file(s) to extract ---" -ForegroundColor Yellow
        
        foreach ($zip in $zipFiles) {
            $zipFullPath = $zip.FullName
            $extractPath = Join-Path $zip.DirectoryName $zip.BaseName
            
            # Mark this file as processed BEFORE we extract it
            $script:processedFiles[$zipFullPath] = $true
            
            Write-Host "$indent Extracting: $($zip.Name)" -ForegroundColor Cyan
            Write-Host "$indent   From: $($zip.DirectoryName)" -ForegroundColor Gray
            
            # Create extraction directory
            try {
                New-Item -ItemType Directory -Path $extractPath -Force -ErrorAction Stop | Out-Null
            } catch {
                Write-Host "$indent   Failed to create directory: $($_.Exception.Message)" -ForegroundColor Red
                continue
            }
            
            # Extract using 7-Zip
            $arguments = @(
                'x',
                "`"$zipFullPath`"",
                "-o`"$extractPath`"",
                '-y'
            )
            
            $processInfo = Start-Process -FilePath $7zipPath -ArgumentList $arguments -Wait -NoNewWindow -PassThru
            
            if ($processInfo.ExitCode -eq 0) {
                Write-Host "$indent   Success" -ForegroundColor Green
                
                # Delete the zip file if requested
                if ($deleteAfterExtract) {
                    try {
                        Remove-Item $zipFullPath -Force
                        Write-Host "$indent   Deleted zip file" -ForegroundColor DarkGray
                    } catch {
                        Write-Host "$indent   Could not delete: $($_.Exception.Message)" -ForegroundColor Yellow
                    }
                }
            } else {
                Write-Host "$indent   Failed to extract (Exit code: $($processInfo.ExitCode))" -ForegroundColor Red
            }
        }
        
        Write-Host ""
    }
    
    Write-Host "$indent No more NEW zip files found" -ForegroundColor Green
}

# Start the extraction process
Write-Host "Starting FULL recursive extraction (turtles all the way down)..." -ForegroundColor Yellow
Write-Host ""

$startTime = Get-Date

Extract-ZipRecursive -sourcePath $rootFolder -deleteAfterExtract $deleteZips

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Extraction complete!" -ForegroundColor Green
Write-Host "Total zip files processed: $($script:processedFiles.Count)" -ForegroundColor Green
Write-Host "Time elapsed: $($duration.ToString('hh\:mm\:ss'))" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
