# Web SOTA start â€” frontend 10814, FastAPI bridge 10815 (see mcp-central-docs WEBAPP_PORTS)
$WebPort = 10814
$BackendPort = 10815
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "Clearing listeners on $WebPort and $BackendPort ..." -ForegroundColor Yellow
$pids = Get-NetTCPConnection -LocalPort $WebPort, $BackendPort -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -gt 4 } | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $pids) {
    Write-Host "Stopping PID $p ..." -ForegroundColor Red
    try { Stop-Process -Id $p -Force -ErrorAction Stop } catch { Write-Host "Could not stop PID $p" -ForegroundColor Gray }
}

Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) { npm install }

Write-Host "Starting backend (uvicorn) on $BackendPort ..." -ForegroundColor Cyan
# Run from repo root with -WorkingDirectory so `uv run` resolves notepadpp_mcp â€” no PYTHONPATH (avoids quoting bugs in -Command).
Start-Process powershell -WorkingDirectory $ProjectRoot -WindowStyle Normal -ArgumentList @(
    "-NoExit"
    "-Command"
    "uv run uvicorn notepadpp_mcp.server:app --host 127.0.0.1 --port $BackendPort --log-level info"
)

$deadline = (Get-Date).AddSeconds(45)
$ready = $false
while ((Get-Date) -lt $deadline) {
    $conn = Get-NetTCPConnection -LocalPort $BackendPort -State Listen -ErrorAction SilentlyContinue
    if ($conn) { $ready = $true; break }
    Start-Sleep -Milliseconds 300
}
if (-not $ready) {
    Write-Host "Backend did not bind to $BackendPort in time. Check the uvicorn window for errors." -ForegroundColor Red
    exit 1
}
Write-Host "Backend is listening on $BackendPort." -ForegroundColor Green

$WebUrl = "http://127.0.0.1:$WebPort/"
Write-Host "Starting Vite on $WebPort (browser opens when dev server is ready) ..." -ForegroundColor Green

# Open default browser once Vite is listening (foreground npm keeps logs in this window).
$openBrowserJob = Start-Job -ScriptBlock {
    param ($Port, $Url)
    $deadline = (Get-Date).AddSeconds(90)
    while ((Get-Date) -lt $deadline) {
        $listen = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        if ($listen) {
            Start-Process $Url
            break
        }
        Start-Sleep -Milliseconds 350
    }
} -ArgumentList $WebPort, $WebUrl

try {

# 4b. Launch background task to open browser once frontend is ready (Auto-opened by Antigravity)
$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
    npm run dev -- --port $WebPort --host 127.0.0.1
}
finally {
    Stop-Job $openBrowserJob -ErrorAction SilentlyContinue
    Remove-Job $openBrowserJob -ErrorAction SilentlyContinue
}


