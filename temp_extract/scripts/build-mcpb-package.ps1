<#
.SYNOPSIS
    Build MCPB package for Notepad++ MCP Server

.DESCRIPTION
    This script builds a production-ready MCPB package for the Notepad++ MCP Server.
    It validates the manifest, builds the package, and optionally signs it.

.PARAMETER NoSign
    Skip package signing (for development/testing)

.PARAMETER OutputDir
    Custom output directory for the built package

.PARAMETER Help
    Show this help message

.EXAMPLE
    .\scripts\build-mcpb-package.ps1
    Build and sign the package (default behavior)

.EXAMPLE
    .\scripts\build-mcpb-package.ps1 -NoSign
    Build without signing (for development)

.EXAMPLE
    .\scripts\build-mcpb-package.ps1 -OutputDir "C:\builds"
    Build with custom output directory

#>

param(
    [switch]$NoSign,
    [string]$OutputDir = "dist",
    [switch]$Help
)

# Show help if requested
if ($Help) {
    Get-Help $PSCommandPath -Detailed
    exit 0
}

# Script configuration
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ManifestPath = Join-Path $ProjectRoot "manifest.json"
$PackageName = "notepadpp-mcp.mcpb"
$Version = "1.2.0"

# Colors for output
function Write-Success { Write-Host "[OK] $args" -ForegroundColor Green }
function Write-Info { Write-Host "[INFO] $args" -ForegroundColor Cyan }
function Write-Warning { Write-Host "[WARN] $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "[ERROR] $args" -ForegroundColor Red }

# Banner
Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Notepad++ MCP Server - MCPB Package Builder v$Version ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check prerequisites
Write-Info "Checking prerequisites..."

# Check if mcpb CLI is installed
if (!(Get-Command mcpb -ErrorAction SilentlyContinue)) {
    Write-Error "MCPB CLI not found. Install with: npm install -g @anthropic-ai/mcpb"
    exit 1
}

$mcpbVersion = mcpb --version
Write-Success "MCPB CLI found: v$mcpbVersion"

# Check if Python is available
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found. Please install Python 3.10 or higher"
    exit 1
}

$pythonVersion = python --version
Write-Success "Python found: $pythonVersion"

# Check if manifest exists
if (!(Test-Path $ManifestPath)) {
    Write-Error "Manifest not found: $ManifestPath"
    exit 1
}

Write-Success "Manifest found: $ManifestPath"

# Step 2: Validate manifest
Write-Info "Validating manifest.json..."

try {
    $validateOutput = mcpb validate $ManifestPath 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Manifest validation failed:"
        Write-Host $validateOutput
        exit 1
    }
    Write-Success "Manifest validation passed"
} catch {
    Write-Error "Manifest validation failed: $_"
    exit 1
}

# Step 3: Create output directory
Write-Info "Creating output directory..."

$OutputPath = Join-Path $ProjectRoot $OutputDir
if (!(Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    Write-Success "Created directory: $OutputPath"
} else {
    Write-Info "Output directory exists: $OutputPath"
}

# Clean old packages
$OldPackages = Get-ChildItem -Path $OutputPath -Filter "*.mcpb" -ErrorAction SilentlyContinue
if ($OldPackages) {
    Write-Info "Cleaning old packages..."
    $OldPackages | Remove-Item -Force
    Write-Success "Removed old packages"
}

# Step 4: Build MCPB package
Write-Info "Building MCPB package..."

$PackageOutput = Join-Path $OutputPath $PackageName

try {
    Push-Location $ProjectRoot
    $buildOutput = mcpb pack . $PackageOutput 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Package build failed:"
        Write-Host $buildOutput
        exit 1
    }
    Pop-Location
    Write-Success "Package built successfully: $PackageOutput"
} catch {
    Pop-Location
    Write-Error "Package build failed: $_"
    exit 1
}

# Step 5: Verify package
Write-Info "Verifying package..."

if (Test-Path $PackageOutput) {
    $packageSize = (Get-Item $PackageOutput).Length / 1MB
    Write-Success "Package verified: $([math]::Round($packageSize, 2)) MB"
} else {
    Write-Error "Package not found after build: $PackageOutput"
    exit 1
}

# Step 6: Sign package (optional)
if (!$NoSign) {
    Write-Warning "Package signing is currently disabled"
    Write-Info "To enable signing, configure MCPB_SIGNING_KEY environment variable"
    # Future implementation:
    # if ($env:MCPB_SIGNING_KEY) {
    #     Write-Info "Signing package..."
    #     mcpb sign --key $env:MCPB_SIGNING_KEY $PackageOutput
    #     Write-Success "Package signed"
    # }
} else {
    Write-Info 'Skipping package signing (development mode)'
}

# Step 7: Display summary
Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║               BUILD COMPLETED SUCCESSFULLY                ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Success "Package: $PackageOutput"
Write-Success "Size: $([math]::Round($packageSize, 2)) MB"
Write-Success "Version: $Version"
Write-Host ""
Write-Info "Next steps:"
Write-Info "1. Test: Drag $PackageName to Claude Desktop"
Write-Info "2. Verify: Configure and test all 26 tools"
Write-Info "3. SOTA Upgrade: Convert individual tools to portmanteau pattern for full compliance"
Write-Info "4. Release: Upload to GitHub releases or distribute directly"
Write-Host ""

