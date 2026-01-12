# Notepad++ MCP Test Runner (PowerShell)
# Quick test runner for Windows development

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("smoke", "standard", "all")]
    [string]$Level = "smoke",

    [switch]$Coverage,
    [switch]$Verbose,
    [switch]$KeepResults,
    [switch]$WithNotepadPP
)

Write-Host "🚀 Notepad++ MCP Megatest Runner" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found in PATH"
    exit 1
}

# Build arguments
$args = @($Level)

if ($Coverage) { $args += "--coverage" }
if ($Verbose) { $args += "--verbose" }
if ($KeepResults) { $args += "--keep-results" }
if ($WithNotepadPP) { $args += "--with-notepadpp" }

# Run the test
try {
    & python "scripts/run_megatest.py" @args
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n🎉 Tests completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "`n💥 Tests failed!" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Error "Test execution failed: $_"
    exit 1
}