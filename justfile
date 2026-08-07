set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

# --- Dashboard ---

# Open the interactive recipe dashboard in the browser
default:
    @just --list


# Synchronize deps, pre-commit hooks, and web frontend
bootstrap:
    uv sync --extra dev --group dev
    uv run pre-commit install
    Set-Location web_sota; npm ci; if ($LASTEXITCODE -ne 0) { npm install }
    Write-Host "Pre-commit hooks installed." -ForegroundColor Green
# --- Quality ---

# Execute Ruff SOTA v13.1 linting
lint:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check .
    Set-Location '{{justfile_directory()}}\web_sota'
    npx @biomejs/biome ci .

# Execute Ruff SOTA v13.1 fix and formatting
fix:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check . --fix --unsafe-fixes
    uv run ruff format .
    Set-Location '{{justfile_directory()}}\web_sota'
    npx @biomejs/biome check --write .

# --- Hardening ---

# Execute Bandit security audit
check-sec:
    Set-Location '{{justfile_directory()}}'
    uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    Set-Location '{{justfile_directory()}}'
    uv run safety check


# Bootstrap: install dev deps + pre-commit hook

# Run CUA-NSIS smoke test (install -> launch -> nav walk -> uninstall)
cua-nsis-test:
    powershell.exe -NoProfile -File "{{justfile_directory()}}\scripts\just\cua-nsis-test.ps1"

# Run CUA webapp test (pre-Tauri: start.ps1 stack + nav walk in browser)
cua-webapp-test:
    powershell.exe -NoProfile -File "{{justfile_directory()}}\scripts\just\cua-webapp-test.ps1"

# Start the full dev stack (backend 10815 + Vite 10814)
serve:
    Set-Location '{{justfile_directory()}}'
    powershell.exe -NoProfile -File "{{justfile_directory()}}\start.ps1"

# Run the test suite (root tests/ - mirrors CI)
test:
    Set-Location '{{justfile_directory()}}'
    uv run python -m pytest tests/ -q --tb=short --no-cov

# Ruff format + Biome write (fix in place)
fmt:
    Set-Location '{{justfile_directory()}}'
    uv run ruff format src/
    uv run ruff check src/ --fix
    Set-Location '{{justfile_directory()}}\web_sota'
    npx @biomejs/biome check --write .

# Package the Claude Desktop .mcpb bundle
mcpb-pack:
    powershell.exe -NoProfile -File "{{justfile_directory()}}\scripts\build-mcpb-package.ps1"

# Build the Tauri NSIS installer (frontend -> PyInstaller -> Rust -> NSIS)
build-native:
    Set-Location '{{justfile_directory()}}\native'
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    .\build.ps1

# Full gate set: lint + typecheck + tests
certify:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check src/
    uv run ruff format src/ --check
    uv run pyright src/
    uv run python -m pytest tests/ -q --tb=short --no-cov
    Set-Location '{{justfile_directory()}}\web_sota'
    npx tsc -b --noEmit
    npx @biomejs/biome ci .
