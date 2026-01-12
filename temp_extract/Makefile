# Notepad++ MCP Server - Development Makefile
# Compatible with Windows (using PowerShell) and Unix-like systems

.PHONY: help install install-dev test test-unit test-integration test-coverage lint format type-check build clean test-install validate-mcpb build-mcpb check all

# Default target
help:
	@echo "Notepad++ MCP Server - Development Commands"
	@echo "=========================================="
	@echo "install-dev    - Install development dependencies"
	@echo "test           - Run tests with coverage"
	@echo "lint           - Run linting checks"
	@echo "format         - Format code with black and isort"
	@echo "type-check     - Run type checking with mypy"
	@echo "build          - Build Python package"
	@echo "build-mcpb     - Build MCPB package"
	@echo "validate-mcpb  - Validate MCPB configuration"
	@echo "test-install   - Test installation in clean environment"
	@echo "clean          - Clean build artifacts"
	@echo "all            - Run all checks and builds"

# Install development dependencies
install-dev:
	python -m pip install --upgrade pip
	pip install -e .[dev]

# Run tests with coverage
test:
	pytest tests/ src/notepadpp_mcp/tests/ -v

# Run unit tests only
test-unit:
	pytest tests/ src/notepadpp_mcp/tests/ -v -m "not integration and not slow"

# Run integration tests only
test-integration:
	pytest tests/ src/notepadpp_mcp/tests/ -v -m integration

# Run tests with coverage
test-coverage:
	pytest tests/ src/notepadpp_mcp/tests/ --cov=src/notepadpp_mcp --cov-report=term-missing --cov-report=html --cov-report=xml

# Run linting checks
lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

# Format code
format:
	ruff format src/ tests/

# Run type checking
type-check:
	python -m mypy src/

# Build Python package
build:
	python -m build

# Build MCPB package
build-mcpb:
	mcpb pack

# Validate MCPB configuration
validate-mcpb:
	mcpb validate

# Test installation in clean environment
test-install:
	python dev.py test-install

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run all checks (lint, format check, type check)
check: lint type-check

# Run all checks and builds
all: lint type-check test-coverage build validate-mcpb build-mcpb

# Windows-specific targets (using PowerShell)
ifeq ($(OS),Windows_NT)
clean:
	powershell -Command "Remove-Item -Recurse -Force build, dist, *.egg-info, htmlcov, .coverage, .pytest_cache, .mypy_cache -ErrorAction SilentlyContinue"
	powershell -Command "Get-ChildItem -Recurse -Directory -Name __pycache__ | Remove-Item -Recurse -Force"
	powershell -Command "Get-ChildItem -Recurse -Filter *.pyc | Remove-Item -Force"
endif
