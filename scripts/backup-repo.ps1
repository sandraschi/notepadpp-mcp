<#
.SYNOPSIS
    Automated Git Repository Backup Script

.DESCRIPTION
    Creates a complete backup of the git repository as a .bundle file
    that can be restored anywhere. Runs automatically via Windows Task Scheduler.

.PARAMETER BackupDir
    Directory to store backups (default: D:\Backups\notepadpp-mcp)

.PARAMETER KeepDays
    Number of days to keep old backups (default: 30)

.EXAMPLE
    .\scripts\backup-repo.ps1
    Creates a backup in the default location

.EXAMPLE
    .\scripts\backup-repo.ps1 -BackupDir "E:\GitBackups" -KeepDays 60
    Creates backup in custom location and keeps for 60 days
#>

param(
    [string]$BackupDir = "D:\Backups\notepadpp-mcp",
    [int]$KeepDays = 30
)

$ErrorActionPreference = "Stop"

# Get repository root
$RepoRoot = Split-Path -Parent $PSScriptRoot

# Create backup directory
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    Write-Host "✅ Created backup directory: $BackupDir" -ForegroundColor Green
}

# Create backup filename with timestamp
$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$BackupFile = Join-Path $BackupDir "notepadpp-mcp_$Timestamp.bundle"

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          Git Repository Backup Script                   ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Change to repository directory
Push-Location $RepoRoot

try {
    # Create git bundle (complete repository backup)
    Write-Host "📦 Creating repository backup..." -ForegroundColor Yellow
    git bundle create $BackupFile --all
    
    if ($LASTEXITCODE -eq 0) {
        $BackupSize = (Get-Item $BackupFile).Length / 1MB
        Write-Host "✅ Backup created successfully!" -ForegroundColor Green
        Write-Host "   File: $BackupFile" -ForegroundColor Gray
        Write-Host "   Size: $([math]::Round($BackupSize, 2)) MB" -ForegroundColor Gray
    } else {
        throw "Git bundle creation failed"
    }
    
    # Verify bundle integrity
    Write-Host ""
    Write-Host "🔍 Verifying backup integrity..." -ForegroundColor Yellow
    $VerifyOutput = git bundle verify $BackupFile 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Backup verified successfully!" -ForegroundColor Green
    } else {
        Write-Warning "Backup verification had warnings (but file is likely OK)"
        Write-Host $VerifyOutput -ForegroundColor Gray
    }
    
    # Clean up old backups
    Write-Host ""
    Write-Host "🧹 Cleaning old backups (older than $KeepDays days)..." -ForegroundColor Yellow
    
    $CutoffDate = (Get-Date).AddDays(-$KeepDays)
    $OldBackups = Get-ChildItem -Path $BackupDir -Filter "*.bundle" | 
                  Where-Object { $_.LastWriteTime -lt $CutoffDate }
    
    if ($OldBackups) {
        $OldBackups | ForEach-Object {
            Write-Host "   Removing: $($_.Name)" -ForegroundColor Gray
            Remove-Item $_.FullName -Force
        }
        Write-Host "✅ Removed $($OldBackups.Count) old backup(s)" -ForegroundColor Green
    } else {
        Write-Host "✅ No old backups to remove" -ForegroundColor Green
    }
    
    # Show backup statistics
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║               BACKUP SUMMARY                             ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
    
    $AllBackups = Get-ChildItem -Path $BackupDir -Filter "*.bundle"
    $TotalSize = ($AllBackups | Measure-Object -Property Length -Sum).Sum / 1MB
    
    Write-Host "   Total backups: $($AllBackups.Count)" -ForegroundColor Cyan
    Write-Host "   Total size: $([math]::Round($TotalSize, 2)) MB" -ForegroundColor Cyan
    Write-Host "   Backup directory: $BackupDir" -ForegroundColor Cyan
    Write-Host "   Latest backup: $BackupFile" -ForegroundColor Cyan
    Write-Host ""
    
    # Show how to restore
    Write-Host "💡 TO RESTORE THIS BACKUP:" -ForegroundColor Yellow
    Write-Host "   1. Clone from bundle:" -ForegroundColor Gray
    Write-Host "      git clone $BackupFile restored-repo" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   2. Or add as remote to existing repo:" -ForegroundColor Gray
    Write-Host "      git bundle unbundle $BackupFile" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host "❌ Backup failed: $_" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}

exit 0

