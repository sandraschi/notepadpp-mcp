#!/usr/bin/env python3
"""
Notepad++ MCP Megatest Runner

Local test runner for development with proper configuration and safety checks.

Usage:
    python scripts/run_megatest.py [level] [options]

Levels:
    smoke       Level 1 - Quick smoke test (2 min)
    standard    Level 2 - Core functionality (10 min)
    advanced    Level 3 - Advanced features (20 min)
    integration Level 4 - Multi-tool workflows (45 min)
    full        Level 5 - Complete validation (90 min)
    all         Run all levels sequentially

Options:
    --with-notepadpp  Run tests that require Notepad++ (if installed)
    --coverage        Generate coverage report
    --verbose         Verbose output
    --keep-results    Keep test artifacts for debugging

Environment Variables:
    MEGATEST_MODE=local|ci         Test environment
    MEGATEST_LOCATION=local|hidden|visible|custom
    MEGATEST_CLEANUP=immediate|on-success|archive
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path


class MegatestRunner:
    """Local megatest runner with safety and convenience features."""

    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.test_dir = self.root_dir / "tests" / "megatest"
        self.results_dir = self.root_dir / "test-results"

        # Ensure test directories exist
        self.results_dir.mkdir(exist_ok=True)

    def check_environment(self):
        """Check if environment is safe for testing."""
        print("Checking test environment...")

        # Check if we're in the right directory
        if not (self.root_dir / "src" / "notepadpp_mcp").exists():
            print("Error: Not in Notepad++ MCP root directory")
            return False

        # Check if tests directory exists
        if not self.test_dir.exists():
            print("Error: Test directory not found")
            return False

        # Check Python version
        if sys.version_info < (3, 10):
            print("Error: Python 3.10+ required")
            return False

        print("Environment check passed")
        return True

    def check_notepadpp(self):
        """Check if Notepad++ is available for testing."""
        try:
            import winreg

            # Try to find Notepad++ in registry
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Notepad++",
            )
            install_path = winreg.QueryValueEx(key, "InstallLocation")[0]
            winreg.CloseKey(key)

            exe_path = Path(install_path) / "notepad++.exe"
            if exe_path.exists():
                print(f"Notepad++ found: {exe_path}")
                return True
            else:
                print("Warning: Notepad++ registry entry found but executable missing")
                return False

        except (FileNotFoundError, OSError):
            print("⚠️  Notepad++ not found in registry")
            return False

    def set_environment_variables(self, args):
        """Set environment variables for testing."""
        os.environ["MEGATEST_MODE"] = "local"
        os.environ["MEGATEST_LOCATION"] = "local"
        os.environ["MEGATEST_CLEANUP"] = (
            "on-success" if args.keep_results else "immediate"
        )

        if args.with_notepadpp and self.check_notepadpp():
            os.environ["NOTEPADPP_AVAILABLE"] = "1"
        else:
            os.environ["NOTEPADPP_AVAILABLE"] = "0"

    def run_pytest(self, test_path, description, timeout=None):
        """Run pytest with proper configuration."""
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(test_path),
            "-v",
            "--tb=short",
            "--strict-markers",
            "--disable-warnings",
            "--durations=10",
        ]

        if hasattr(self, "args") and self.args.coverage:
            cmd.extend(
                [
                    "--cov=src/notepadpp_mcp",
                    "--cov-report=html",
                    "--cov-report=term-missing",
                    f"--cov-report=html:{self.results_dir / 'coverage'}",
                ]
            )

        print(f"\nRunning {description}...")
        print(f"Command: {' '.join(cmd)}")

        start_time = time.time()

        try:
            result = subprocess.run(
                cmd, cwd=self.root_dir, timeout=timeout, capture_output=False
            )

            duration = time.time() - start_time
            print(f"Duration: {duration:.2f}s")
            if result.returncode == 0:
                print(f"PASSED: {description}")
                return True
            else:
                print(f"FAILED: {description} (exit code: {result.returncode})")
                return False

        except subprocess.TimeoutExpired:
            print(f"TIMED OUT: {description} after {timeout}s")
            return False

    def run_level_1_smoke(self):
        """Run Level 1: Smoke Test."""
        test_path = self.test_dir / "level1_smoke"
        return self.run_pytest(test_path, "Level 1 - Smoke Test", timeout=180)

    def run_level_2_standard(self):
        """Run Level 2: Standard Test."""
        test_path = self.test_dir / "level2_standard"
        return self.run_pytest(test_path, "Level 2 - Standard Test", timeout=900)

    def run_level_3_advanced(self):
        """Run Level 3: Advanced Test."""
        test_path = self.test_dir / "level3_advanced"
        if not test_path.exists():
            print("⚠️  Level 3 tests not implemented yet")
            return True
        return self.run_pytest(test_path, "Level 3 - Advanced Test", timeout=1800)

    def run_level_4_integration(self):
        """Run Level 4: Integration Test."""
        test_path = self.test_dir / "level4_integration"
        if not test_path.exists():
            print("⚠️  Level 4 tests not implemented yet")
            return True
        return self.run_pytest(test_path, "Level 4 - Integration Test", timeout=3600)

    def run_level_5_full(self):
        """Run Level 5: Full Blast Test."""
        test_path = self.test_dir / "level5_full"
        if not test_path.exists():
            print("⚠️  Level 5 tests not implemented yet")
            return True
        return self.run_pytest(test_path, "Level 5 - Full Blast Test", timeout=7200)

    def run_all_levels(self):
        """Run all test levels sequentially."""
        levels = [
            ("Level 1 - Smoke", self.run_level_1_smoke),
            ("Level 2 - Standard", self.run_level_2_standard),
            ("Level 3 - Advanced", self.run_level_3_advanced),
            ("Level 4 - Integration", self.run_level_4_integration),
            ("Level 5 - Full", self.run_level_5_full),
        ]

        results = []
        for name, func in levels:
            result = func()
            results.append((name, result))

            # Stop on first failure unless explicitly requested
            if not result and not self.args.force_continue:
                print(f"\nStopping at {name} failure")
                break

        print("\nTest Results Summary:")
        for name, result in results:
            status = "PASSED" if result else "FAILED"
            print(f"  {name}: {status}")

        all_passed = all(result for _, result in results)
        return all_passed

    def run_specific_level(self, level):
        """Run a specific test level."""
        level_map = {
            "smoke": self.run_level_1_smoke,
            "1": self.run_level_1_smoke,
            "standard": self.run_level_2_standard,
            "2": self.run_level_2_standard,
            "advanced": self.run_level_3_advanced,
            "3": self.run_level_3_advanced,
            "integration": self.run_level_4_integration,
            "4": self.run_level_4_integration,
            "full": self.run_level_5_full,
            "5": self.run_level_5_full,
        }

        if level not in level_map:
            print(f"Unknown level: {level}")
            print("Available levels: smoke, standard, advanced, integration, full, all")
            return False

        return level_map[level]()

    def main(self):
        """Main entry point."""
        parser = argparse.ArgumentParser(
            description="Notepad++ MCP Megatest Runner",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=__doc__,
        )

        parser.add_argument(
            "level",
            nargs="?",
            default="standard",
            choices=[
                "smoke",
                "1",
                "standard",
                "2",
                "advanced",
                "3",
                "integration",
                "4",
                "full",
                "5",
                "all",
            ],
            help="Test level to run",
        )

        parser.add_argument(
            "--with-notepadpp",
            action="store_true",
            help="Include tests that require Notepad++",
        )

        parser.add_argument(
            "--coverage", action="store_true", help="Generate coverage report"
        )

        parser.add_argument(
            "--verbose", "-v", action="store_true", help="Verbose output"
        )

        parser.add_argument(
            "--keep-results",
            action="store_true",
            help="Keep test artifacts for debugging",
        )

        parser.add_argument(
            "--force-continue",
            action="store_true",
            help="Continue running all levels even if some fail",
        )

        self.args = parser.parse_args()

        print("Notepad++ MCP Megatest Runner")
        print("=" * 50)

        # Environment check
        if not self.check_environment():
            return 1

        # Set environment
        self.set_environment_variables(self.args)

        # Run tests
        start_time = time.time()

        try:
            if self.args.level == "all":
                success = self.run_all_levels()
            else:
                success = self.run_specific_level(self.args.level)

            duration = time.time() - start_time

            print(f"\nTotal runtime: {duration:.1f}s")

            if success:
                print("All tests passed!")
                return 0
            else:
                print("Some tests failed!")
                return 1

        except KeyboardInterrupt:
            print("\nInterrupted by user")
            return 130
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            return 1


if __name__ == "__main__":
    runner = MegatestRunner()
    sys.exit(runner.main())
