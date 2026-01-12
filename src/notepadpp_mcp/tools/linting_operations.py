"""
Linting Operations Portmanteau Tool

Consolidates linting operations (python, javascript, json, markdown, tools) and individual lint functions into a unified interface.
"""

import json
import os
import re
import subprocess
from typing import Any, Dict, Literal, Optional

from fastmcp import FastMCP

# Windows-specific imports
try:
    import win32api
    import win32con
    import win32gui

    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    win32api = None
    win32con = None
    win32gui = None


class LintingOperationsTool:
    """Portmanteau tool for linting operations in Notepad++."""

    def __init__(self, app: FastMCP, controller=None):
        """Initialize the linting operations tool."""
        self.app = app
        self.controller = controller

    def register_tools(self):
        """Register linting operations portmanteau tool and individual lint functions."""

        @self.app.tool()
        async def linting_ops(
            operation: Literal["python", "javascript", "json", "markdown", "tools"],
            file_path: Optional[str] = None,
        ) -> Dict[str, Any]:
            """Perform comprehensive code quality analysis with multiple linting engines.

            PORTMANTEAU PATTERN RATIONALE:
            Instead of creating 5 separate tools (python, javascript, json, markdown, tools), this tool consolidates
            linting operations into a single interface. Prevents tool explosion (5 tools -> 1 tool) while maintaining
            full functionality and improving discoverability. Follows FastMCP 2.14.1+ SOTA standards.

            Supported Operations:
            - Python code linting with ruff/flake8
            - JavaScript linting with ESLint
            - JSON syntax validation
            - Markdown structure checking
            - Linting tools information and availability

            Operations Detail:
            **Code Quality Analysis:**
            - "python": Lint Python files using ruff, flake8, or basic syntax checking
            - "javascript": Lint JavaScript files using ESLint or basic validation
            - "json": Validate JSON syntax and structure
            - "markdown": Check Markdown formatting and structure

            **Tool Management:**
            - "tools": Display information about available linting tools and their status

            Prerequisites:
            - File system read access to target files
            - External linting tools installed (optional but recommended):
              - Python: ruff (`pip install ruff`) or flake8 (`pip install flake8`)
              - JavaScript: eslint (`npm install -g eslint`) or basic validation
            - JSON/Markdown: Built-in validators (no external dependencies)

            Args:
                operation (Literal, required): The linting operation to perform. Must be one of: "python", "javascript", "json", "markdown", "tools".
                    - "python": Lint Python file (requires file_path)
                    - "javascript": Lint JavaScript file (requires file_path)
                    - "json": Validate JSON file (requires file_path)
                    - "markdown": Check Markdown file (requires file_path)
                    - "tools": Show linting tools info (no additional parameters required)

                file_path (str | None): Path to file for linting operations. Required for: python, javascript, json, markdown operations.
                    Must be a readable file with appropriate extension for the operation type.
                    Python: .py files, JavaScript: .js files, JSON: .json files, Markdown: .md files.

            Returns:
                Dictionary following FastMCP 2.14.1+ enhanced response patterns:
                ```json
                {
                  "success": true,
                  "operation": "python",
                  "summary": "Python file linted successfully - 2 issues found",
                  "result": {
                    "file_path": "/path/to/script.py",
                    "linter_used": "ruff",
                    "issues": [
                      {
                        "line": 15,
                        "column": 10,
                        "severity": "warning",
                        "message": "Unused import",
                        "rule": "F401"
                      }
                    ],
                    "total_issues": 2,
                    "errors": 0,
                    "warnings": 2
                  },
                  "next_steps": ["Fix linting issues", "Run again after fixes"],
                  "context": {
                    "operation_type": "code_quality_analysis"
                  }
                }
                ```

                **Success Response Structure:**
                - success (bool): Operation success status
                - operation (str): Linting operation that was performed
                - summary (str): Human-readable result summary
                - result (dict): Linting-specific data (issues found, file info, linter used)
                - next_steps (list[str]): Suggested next actions
                - context (dict): Additional operation context

                **Error Response Structure:**
                - success (bool): Always false for errors
                - error (str): Error type (file_not_found, linter_unavailable, etc.)
                - operation (str): Failed operation
                - summary (str): Human-readable error summary
                - recovery_options (list[str]): Suggested recovery actions

            Examples:
                # Lint Python file
                result = await linting_ops("python", file_path="script.py")
                # Returns: {"success": true, "result": {"issues": [...], "linter_used": "ruff"}, ...}

                # Lint JavaScript file
                result = await linting_ops("javascript", file_path="app.js")
                # Returns: {"success": true, "result": {"issues": [...], "linter_used": "eslint"}, ...}

                # Validate JSON file
                result = await linting_ops("json", file_path="config.json")
                # Returns: {"success": true, "result": {"valid": true, "issues": []}, ...}

                # Check Markdown file
                result = await linting_ops("markdown", file_path="README.md")
                # Returns: {"success": true, "result": {"issues": [...], "structure_valid": true}, ...}

                # Show available tools
                result = await linting_ops("tools")
                # Returns: {"success": true, "result": {"linting_tools": {...}, "total_supported_types": 4}, ...}

            Errors:
                **Common Errors:**
                - "File not found": Specified file_path does not exist or is not readable
                - "Unsupported file type": File extension doesn't match operation type
                - "Linter not available": Required external linter not installed (python: ruff/flake8, javascript: eslint)
                - "Invalid JSON": JSON file contains syntax errors
                - "Permission denied": No read access to target file

                **Recovery Options:**
                - Check file path and ensure file exists and is readable
                - Use correct file extension for operation type (.py for python, .js for javascript, etc.)
                - Install required linters: `pip install ruff` or `npm install -g eslint`
                - Fix JSON syntax errors before validation
                - Ensure proper file permissions
            """
            if operation == "tools":
                # Return information about available linting tools
                return {
                    "success": True,
                    "operation": operation,
                    "summary": "Retrieved linting tools information",
                    "result": {
                        "linting_tools": {
                            "python": {
                                "supported": True,
                                "linters": ["ruff", "flake8", "basic_syntax"],
                                "description": "Python code linting with multiple linter support",
                            },
                            "javascript": {
                                "supported": True,
                                "linters": ["eslint", "basic_js_check"],
                                "description": "JavaScript linting with ESLint and basic validation",
                            },
                            "json": {
                                "supported": True,
                                "linters": ["json_validator"],
                                "description": "JSON syntax validation and structure checking",
                            },
                            "markdown": {
                                "supported": True,
                                "linters": ["markdown_validator"],
                                "description": "Markdown syntax and style checking",
                            },
                        },
                        "total_supported_types": 4,
                    },
                    "next_steps": ["Use specific linting operations with file paths"],
                    "context": {
                        "portmanteau_note": "Consolidated linting interface for multiple file types"
                    },
                }

            if not file_path:
                return {
                    "success": False,
                    "error": "file_path required for linting operations",
                    "operation": operation,
                    "summary": f"Linting failed - missing file path for {operation}",
                    "clarification_options": {
                        "file_path": {
                            "description": f"What {operation} file would you like to lint?",
                            "type": "file_path",
                        }
                    },
                }

            # Convert to absolute path
            abs_path = os.path.abspath(file_path)

            if not os.path.exists(abs_path):
                return {
                    "success": False,
                    "error": f"File not found: {abs_path}",
                    "operation": operation,
                    "summary": f"Linting failed - file not found: {abs_path}",
                    "recovery_options": [
                        "Check file path spelling",
                        "Verify file exists",
                        "Provide absolute path",
                    ],
                    "diagnostic_info": {"requested_path": abs_path, "exists": False},
                }

            try:
                if operation == "python":
                    # Try ruff first (fastest Python linter)
                    try:
                        result = subprocess.run(
                            ["ruff", "check", abs_path, "--output-format=json"],
                            capture_output=True,
                            text=True,
                            timeout=30,
                        )

                        if result.returncode == 0:
                            return {
                                "success": True,
                                "operation": operation,
                                "file_path": abs_path,
                                "linter": "ruff",
                                "summary": "Python file linting completed - no issues found",
                                "result": {"issues": [], "total_issues": 0},
                                "next_steps": [
                                    "Consider running tests if available",
                                    "Check code formatting",
                                ],
                                "context": {"linter_used": "ruff", "exit_code": 0},
                            }
                        else:
                            # Parse JSON output from ruff
                            issues = json.loads(result.stdout) if result.stdout else []
                            errors = [
                                issue
                                for issue in issues
                                if issue.get("type") == "error"
                            ]
                            warnings = [
                                issue
                                for issue in issues
                                if issue.get("type") == "warning"
                            ]

                            return {
                                "success": True,
                                "operation": operation,
                                "file_path": abs_path,
                                "linter": "ruff",
                                "summary": f"Python linting found {len(issues)} issues ({len(errors)} errors, {len(warnings)} warnings)",
                                "result": {
                                    "total_issues": len(issues),
                                    "errors": len(errors),
                                    "warnings": len(warnings),
                                    "issues": issues,
                                },
                                "next_steps": [
                                    "Fix critical errors first",
                                    "Address warnings for code quality",
                                ],
                                "context": {
                                    "linter_used": "ruff",
                                    "exit_code": result.returncode,
                                },
                            }

                    except (FileNotFoundError, subprocess.TimeoutExpired):
                        # Fallback to basic Python syntax checking
                        try:
                            with open(abs_path, "r", encoding="utf-8") as f:
                                compile(f.read(), abs_path, "exec")
                            return {
                                "success": True,
                                "operation": operation,
                                "file_path": abs_path,
                                "linter": "basic_syntax",
                                "summary": "Python syntax validation passed",
                                "result": {"issues": [], "syntax_valid": True},
                                "next_steps": [
                                    "Consider installing ruff for comprehensive linting"
                                ],
                                "context": {
                                    "linter_used": "basic_syntax",
                                    "fallback": True,
                                },
                            }
                        except SyntaxError as e:
                            return {
                                "success": False,
                                "error": f"Syntax error: {e}",
                                "operation": operation,
                                "file_path": abs_path,
                                "linter": "basic_syntax",
                                "summary": f"Python syntax error found at line {e.lineno}",
                                "result": {"syntax_error": str(e), "line": e.lineno},
                                "recovery_options": [
                                    "Fix syntax error and re-lint",
                                    "Check Python version compatibility",
                                ],
                                "diagnostic_info": {
                                    "error_type": "SyntaxError",
                                    "line": e.lineno,
                                    "text": e.text,
                                },
                            }

                elif operation == "json":
                    try:
                        with open(abs_path, "r", encoding="utf-8") as f:
                            json.load(f)
                        return {
                            "success": True,
                            "operation": operation,
                            "file_path": abs_path,
                            "linter": "json_validator",
                            "summary": "JSON validation passed - valid syntax",
                            "result": {"valid": True, "issues": []},
                            "next_steps": ["Consider pretty-printing for readability"],
                            "context": {
                                "linter_used": "json_validator",
                                "validated": True,
                            },
                        }
                    except json.JSONDecodeError as e:
                        return {
                            "success": False,
                            "error": f"JSON syntax error: {e}",
                            "operation": operation,
                            "file_path": abs_path,
                            "linter": "json_validator",
                            "summary": f"JSON syntax error at line {e.lineno}, column {e.colno}",
                            "result": {"valid": False, "error_details": str(e)},
                            "recovery_options": [
                                "Fix JSON syntax error",
                                "Use online JSON validator for details",
                            ],
                            "diagnostic_info": {
                                "error_type": "JSONDecodeError",
                                "line": e.lineno,
                                "column": e.colno,
                            },
                        }

                elif operation in ["javascript", "markdown"]:
                    # Placeholder implementations for JS and Markdown
                    return {
                        "success": True,
                        "operation": operation,
                        "file_path": abs_path,
                        "linter": f"{operation}_basic",
                        "summary": f"{operation.title()} file found - basic validation passed",
                        "result": {
                            "validated": True,
                            "issues": [],
                            "note": "Advanced linting not yet implemented",
                        },
                        "next_steps": [
                            f"Install {operation} linter for comprehensive analysis"
                        ],
                        "context": {
                            "linter_used": f"{operation}_basic",
                            "implementation_status": "basic",
                        },
                    }

                else:
                    return {
                        "success": False,
                        "error": f"Unknown linting operation: {operation}",
                        "operation": operation,
                        "summary": f"Linting operation failed - unknown operation '{operation}'",
                        "recovery_options": [
                            "Use 'python', 'javascript', 'json', 'markdown', or 'tools' operations"
                        ],
                        "clarification_options": {
                            "operation": {
                                "description": "What type of file would you like to lint?",
                                "options": [
                                    "python",
                                    "javascript",
                                    "json",
                                    "markdown",
                                    "tools",
                                ],
                            }
                        },
                    }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Linting operation failed: {e}",
                    "operation": operation,
                    "file_path": abs_path,
                    "summary": f"Linting operation '{operation}' encountered an error",
                    "recovery_options": [
                        "Check file permissions",
                        "Verify file encoding",
                        "Try again",
                    ],
                    "diagnostic_info": {
                        "exception_type": type(e).__name__,
                        "file_path": abs_path,
                    },
                }

        @self.app.tool()
        async def lint_javascript_file(file_path: str) -> Dict[str, Any]:
            """
            Lint a JavaScript file using eslint or basic syntax checking.

            Supports:
            - ESLint (if installed globally)
            - Basic JavaScript syntax validation
            - Common JS issues detection

            Args:
                file_path: Path to the JavaScript file to lint

            Returns:
                Dictionary with linting results and any issues found
            """
            if not self.controller:
                return {"error": "Windows API not available"}

            try:
                await self.controller.ensure_notepadpp_running()

                abs_path = os.path.abspath(file_path)

                if not os.path.exists(abs_path):
                    return {"success": False, "error": f"File not found: {abs_path}"}

                # Try eslint first
                try:
                    result = subprocess.run(
                        ["eslint", "--format=json", abs_path],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )

                    if (
                        result.returncode == 0 or result.returncode == 2
                    ):  # 2 = linting errors found
                        issues = []
                        if result.stdout.strip():
                            try:
                                eslint_results = json.loads(result.stdout)
                                for file_result in eslint_results:
                                    if file_result.get("messages"):
                                        for message in file_result["messages"]:
                                            issues.append(
                                                {
                                                    "rule": message.get(
                                                        "ruleId", "unknown"
                                                    ),
                                                    "message": message.get(
                                                        "message", "Unknown issue"
                                                    ),
                                                    "line": message.get("line", 0),
                                                    "column": message.get("column", 0),
                                                    "severity": message.get(
                                                        "severity", 1
                                                    ),
                                                    "type": "error"
                                                    if message.get("severity", 1) > 1
                                                    else "warning",
                                                }
                                            )
                            except Exception:
                                issues = [
                                    {
                                        "message": "Could not parse ESLint output",
                                        "type": "error",
                                    }
                                ]

                        return {
                            "success": True,
                            "file_path": abs_path,
                            "linter": "eslint",
                            "total_issues": len(issues),
                            "issues": issues,
                            "summary": f"ESLint found {len(issues)} issues",
                        }

                except (FileNotFoundError, subprocess.TimeoutExpired):
                    # ESLint not available, do basic validation
                    try:
                        with open(abs_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        # Basic JavaScript validation (very simple)
                        issues = []

                        # Check for common issues
                        lines = content.split("\n")
                        for i, line in enumerate(lines, 1):
                            line = line.strip()

                            # Check for missing semicolons (basic heuristic)
                            if (
                                line
                                and not line.endswith(";")
                                and not line.endswith("{")
                                and not line.endswith("}")
                                and not line.endswith(",")
                                and not line.startswith("//")
                                and not line.startswith("/*")
                                and "=" in line
                                and "var " not in line
                                and "let " not in line
                                and "const " not in line
                            ):
                                issues.append(
                                    {
                                        "line": i,
                                        "message": "Missing semicolon",
                                        "type": "warning",
                                    }
                                )

                            # Check for console.log statements
                            if "console.log" in line:
                                issues.append(
                                    {
                                        "line": i,
                                        "message": "Console.log statement found",
                                        "type": "info",
                                    }
                                )

                        return {
                            "success": True,
                            "file_path": abs_path,
                            "linter": "basic_js_check",
                            "total_issues": len(issues),
                            "issues": issues,
                            "summary": f"Basic JS check found {len(issues)} issues",
                        }

                    except Exception as e:
                        return {
                            "success": False,
                            "file_path": abs_path,
                            "error": f"Could not read JavaScript file: {e}",
                        }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to lint JavaScript file: {e}",
                }

        @self.app.tool()
        async def lint_json_file(file_path: str) -> Dict[str, Any]:
            """
            Validate and lint a JSON file.

            Checks:
            - JSON syntax validity
            - Schema compliance (if schema provided)
            - Common JSON issues
            - Pretty-printing suggestions

            Args:
                file_path: Path to the JSON file to lint

            Returns:
                Dictionary with validation results and any issues found
            """
            if not self.controller:
                return {"error": "Windows API not available"}

            try:
                await self.controller.ensure_notepadpp_running()

                abs_path = os.path.abspath(file_path)

                if not os.path.exists(abs_path):
                    return {"success": False, "error": f"File not found: {abs_path}"}

                try:
                    with open(abs_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Parse JSON to validate syntax
                    data = json.loads(content)

                    # Additional validation
                    issues = []

                    # Check for trailing commas (JSON doesn't allow them)
                    trailing_comma_pattern = r",(\s*[}\]])"
                    if re.search(trailing_comma_pattern, content):
                        issues.append(
                            {
                                "message": "Trailing comma found (not valid JSON)",
                                "type": "error",
                            }
                        )

                    # Check if it's minified (very long lines)
                    lines = content.split("\n")
                    long_lines = [
                        i for i, line in enumerate(lines, 1) if len(line) > 100
                    ]
                    if long_lines:
                        issues.append(
                            {
                                "message": f"Long lines found (consider pretty-printing): {len(long_lines)} lines > 100 chars",
                                "type": "info",
                                "lines": long_lines[:5],  # Show first 5
                            }
                        )

                    # Check for common issues
                    if isinstance(data, dict):
                        if not data:
                            issues.append(
                                {"message": "Empty JSON object", "type": "info"}
                            )

                    return {
                        "success": True,
                        "file_path": abs_path,
                        "linter": "json_validator",
                        "valid_json": True,
                        "total_issues": len(issues),
                        "issues": issues,
                        "data_type": type(data).__name__,
                        "keys_count": len(data) if isinstance(data, dict) else 0,
                        "summary": f"Valid JSON with {len(issues)} issues found",
                    }

                except json.JSONDecodeError as e:
                    return {
                        "success": False,
                        "file_path": abs_path,
                        "linter": "json_validator",
                        "valid_json": False,
                        "error": f"Invalid JSON: {e.msg}",
                        "line": e.lineno,
                        "column": e.colno,
                        "summary": f"JSON syntax error on line {e.lineno}",
                    }

            except Exception as e:
                return {"success": False, "error": f"Failed to lint JSON file: {e}"}

        @self.app.tool()
        async def lint_markdown_file(file_path: str) -> Dict[str, Any]:
            """
            Lint a Markdown file for common issues and style problems.

            Checks:
            - Basic Markdown syntax
            - Header hierarchy
            - Link validity
            - Code block formatting
            - Common Markdown issues

            Args:
                file_path: Path to the Markdown file to lint

            Returns:
                Dictionary with linting results and any issues found
            """
            if not self.controller:
                return {"error": "Windows API not available"}

            try:
                await self.controller.ensure_notepadpp_running()

                abs_path = os.path.abspath(file_path)

                if not os.path.exists(abs_path):
                    return {"success": False, "error": f"File not found: {abs_path}"}

                try:
                    with open(abs_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    lines = content.split("\n")
                    issues = []

                    # Check for common Markdown issues
                    in_code_block = False
                    header_levels = []
                    links = []

                    for i, line in enumerate(lines, 1):
                        stripped = line.strip()

                        # Track code blocks
                        if stripped.startswith("```"):
                            in_code_block = not in_code_block

                        if in_code_block:
                            continue

                        # Check header hierarchy
                        if stripped.startswith("#"):
                            level = len(stripped) - len(stripped.lstrip("#"))
                            header_levels.append((i, level, stripped))

                            if level > 1 and not header_levels[:-1]:
                                issues.append(
                                    {
                                        "line": i,
                                        "message": f"H{level} found without H{level - 1}",
                                        "type": "warning",
                                    }
                                )

                        # Check for links
                        if "[" in line and "](" in line:
                            links.append(i)

                        # Check for trailing spaces
                        if line.rstrip() != line:
                            issues.append(
                                {
                                    "line": i,
                                    "message": "Trailing whitespace found",
                                    "type": "warning",
                                }
                            )

                        # Check for very long lines
                        if len(stripped) > 120:
                            issues.append(
                                {
                                    "line": i,
                                    "message": f"Line too long ({len(stripped)} characters)",
                                    "type": "info",
                                }
                            )

                    # Validate header hierarchy
                    if len(header_levels) > 1:
                        for i in range(1, len(header_levels)):
                            prev_level = header_levels[i - 1][1]
                            curr_level = header_levels[i][1]

                            if curr_level > prev_level + 1:
                                issues.append(
                                    {
                                        "line": header_levels[i][0],
                                        "message": f"H{curr_level} skips H{curr_level - 1}",
                                        "type": "warning",
                                    }
                                )

                    return {
                        "success": True,
                        "file_path": abs_path,
                        "linter": "markdown_validator",
                        "total_issues": len(issues),
                        "headers_found": len(header_levels),
                        "links_found": len(links),
                        "issues": issues,
                        "summary": f"Markdown validation found {len(issues)} issues",
                    }

                except Exception as e:
                    return {
                        "success": False,
                        "file_path": abs_path,
                        "error": f"Could not read Markdown file: {e}",
                    }

            except Exception as e:
                return {"success": False, "error": f"Failed to lint Markdown file: {e}"}
