#!/usr/bin/env python3
"""
Development helper script for notepadpp-mcp.
Provides common development tasks.
"""

import logging
import subprocess
import sys
import os
from pathlib import Path

# Configure structured logging for development script
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(console_handler)

def run_command(cmd, check=True):
    """Run command and handle errors."""
    logger.info(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=check)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        return False

def install_dev():
    """Install development dependencies."""
    logger.info("Installing development dependencies...")
    return run_command([sys.executable, "-m", "pip", "install", "-e", ".[dev]"])

def run_tests():
    """Run test suite."""
    logger.info("Running tests...")
    return run_command([sys.executable, "-m", "pytest", "-v"])

def run_type_check():
    """Run type checking."""
    logger.info("Running type checks...")
    return run_command([sys.executable, "-m", "mypy", "src"])

def format_code():
    """Format code with black and isort."""
    logger.info("Formatting code...")
    success = True
    success &= run_command([sys.executable, "-m", "black", "src", "tests"])
    success &= run_command([sys.executable, "-m", "isort", "src", "tests"])
    return success

def lint_code():
    """Run linting checks."""
    logger.info("Running linting...")
    success = True
    success &= run_command([sys.executable, "-m", "black", "--check", "src", "tests"])
    success &= run_command([sys.executable, "-m", "isort", "--check-only", "src", "tests"])
    return success

def build_package():
    """Build package for distribution."""
    logger.info("Building package...")
    return run_command([sys.executable, "-m", "build"])

def test_install():
    """Test installation in clean environment."""
    logger.info("Testing installation...")
    # Create temporary virtual environment
    venv_path = Path("test_venv")
    if venv_path.exists():
        import shutil
        shutil.rmtree(venv_path)
    
    success = True
    success &= run_command([sys.executable, "-m", "venv", str(venv_path)])
    
    if os.name == 'nt':  # Windows
        pip_path = venv_path / "Scripts" / "pip.exe"
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    success &= run_command([str(pip_path), "install", "."])
    success &= run_command([str(python_path), "-c", "import notepadpp_mcp; logger.info('Import successful')"])
    
    # Cleanup
    import shutil
    shutil.rmtree(venv_path)
    
    return success

def validate_dxt():
    """Validate DXT configuration."""
    logger.info("Validating DXT configuration...")
    return run_command(["dxt", "validate"])

def build_dxt():
    """Build DXT package."""
    logger.info("Building DXT package...")
    return run_command(["dxt", "pack"])

def main():
    """Main development script."""
    if len(sys.argv) < 2:
        logger.info("Usage: python dev.py <command>")
        logger.info("Commands:")
        logger.info("  install-dev  - Install development dependencies")
        logger.info("  test         - Run tests")
        logger.info("  type-check   - Run type checking")
        logger.info("  format       - Format code")
        logger.info("  lint         - Run linting")
        logger.info("  build        - Build package")
        logger.info("  test-install - Test installation")
        logger.info("  validate-dxt - Validate DXT config")
        logger.info("  build-dxt    - Build DXT package")
        logger.info("  all          - Run all checks")
        return 1
    
    command = sys.argv[1]
    
    if command == "install-dev":
        return 0 if install_dev() else 1
    elif command == "test":
        return 0 if run_tests() else 1
    elif command == "type-check":
        return 0 if run_type_check() else 1
    elif command == "format":
        return 0 if format_code() else 1
    elif command == "lint":
        return 0 if lint_code() else 1
    elif command == "build":
        return 0 if build_package() else 1
    elif command == "test-install":
        return 0 if test_install() else 1
    elif command == "validate-dxt":
        return 0 if validate_dxt() else 1
    elif command == "build-dxt":
        return 0 if build_dxt() else 1
    elif command == "all":
        success = True
        success &= lint_code()
        success &= run_type_check()
        success &= run_tests()
        success &= test_install()
        success &= validate_dxt()
        return 0 if success else 1
    else:
        logger.info(f"Unknown command: {command}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
