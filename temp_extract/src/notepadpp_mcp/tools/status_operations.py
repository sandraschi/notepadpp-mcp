"""
Status Operations Portmanteau Tool

Consolidates status operations (help, system_status, health_check) into a unified interface.
"""

import time
from typing import Any, Dict, Literal, Optional

from fastmcp import FastMCP

# Windows-specific imports
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Constants (should be imported from main module)
NOTEPADPP_TIMEOUT = 10
NOTEPADPP_AUTO_START = True


class StatusOperationsTool:
    """Portmanteau tool for status operations in Notepad++."""

    def __init__(self, app: FastMCP, controller=None, logger=None):
        """Initialize the status operations tool."""
        self.app = app
        self.controller = controller
        self.logger = logger

    def register_tools(self):
        """Register status operations portmanteau tool."""

        @self.app.tool()
        async def status_ops(
            operation: Literal["help", "system_status", "health_check"],
            category: str = "",
            tool_name: str = ""
        ) -> Dict[str, Any]:
            """
            PORTMANTEAU PATTERN RATIONALE:
            Consolidates status operations (help, system_status, health_check) into single interface. Prevents tool explosion while maintaining
            full functionality. Follows FastMCP 2.13+ best practices.

            Args:
                operation: Status operation to perform ("help", "system_status", "health_check")
                category: Help category filter (for "help" operation)
                tool_name: Specific tool name (for "help" operation)

            Returns:
                Dictionary with operation results and enhanced response metadata
            """
            if operation == "help":
                return await self._handle_help(category, tool_name)

            elif operation == "system_status":
                return await self._handle_system_status()

            elif operation == "health_check":
                return await self._handle_health_check()

            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "operation": operation,
                    "summary": f"Status operation failed - unknown operation '{operation}'",
                    "recovery_options": ["Use 'help', 'system_status', or 'health_check' operations"],
                    "clarification_options": {
                        "operation": {
                            "description": "What status operation would you like to perform?",
                            "options": ["help", "system_status", "health_check"]
                        }
                    }
                }

    async def _handle_help(self, category: str, tool_name: str) -> Dict[str, Any]:
        """Handle help operation."""
        try:
            # Define tool categories and their tools (updated for portmanteau pattern)
            help_data = {
                "file_operations": {
                    "description": "File management operations",
                    "tools": {
                        "file_ops": "Consolidated file operations (open, new, save, info)",
                    },
                },
                "text_operations": {
                    "description": "Text manipulation and editing",
                    "tools": {
                        "text_ops": "Consolidated text operations (insert, find)",
                    },
                },
                "status_operations": {
                    "description": "System and application status",
                    "tools": {
                        "status_ops": "Consolidated status operations (help, system_status, health_check)",
                    },
                },
                "tab_operations": {
                    "description": "Tab management",
                    "tools": {
                        "tab_ops": "Consolidated tab operations (list, switch, close)",
                    },
                },
                "session_operations": {
                    "description": "Session management",
                    "tools": {
                        "session_ops": "Consolidated session operations (save, load, list)",
                    },
                },
                "linting_operations": {
                    "description": "Code quality analysis",
                    "tools": {
                        "linting_ops": "Consolidated linting operations (python, js, json, markdown)",
                    },
                },
                "display_operations": {
                    "description": "Display and theme fixes",
                    "tools": {
                        "display_ops": "Consolidated display operations (invisible text, display issues)",
                    },
                },
                "plugin_operations": {
                    "description": "Plugin ecosystem management",
                    "tools": {
                        "plugin_ops": "Consolidated plugin operations (discover, install, list, execute)",
                    },
                },
            }

            if not category:
                # Return all categories
                return {
                    "success": True,
                    "operation": "help",
                    "summary": "Available tool categories",
                    "result": {
                        "categories": list(help_data.keys()),
                        "total_tools": sum(len(cat["tools"]) for cat in help_data.values()),
                        "system": "Portmanteau pattern - consolidated tools"
                    },
                    "next_steps": ["Specify category to see tools", "Use tool_name for detailed help"],
                    "context": {"help_system": "Multilevel Help System", "pattern": "portmanteau"}
                }

            if category not in help_data:
                available_categories = list(help_data.keys())
                return {
                    "success": False,
                    "error": f"Unknown category '{category}'",
                    "operation": "help",
                    "summary": f"Help category '{category}' not found",
                    "recovery_options": ["Choose from available categories"],
                    "clarification_options": {
                        "category": {
                            "description": "What category would you like help with?",
                            "options": available_categories
                        }
                    },
                    "context": {"available_categories": available_categories}
                }

            category_data = help_data[category]

            if not tool_name:
                # Return tools in category
                return {
                    "success": True,
                    "operation": "help",
                    "summary": f"Tools in category: {category}",
                    "result": {
                        "category": category,
                        "description": category_data["description"],
                        "tools": category_data["tools"],
                        "tool_count": len(category_data["tools"])
                    },
                    "next_steps": ["Specify tool_name for detailed help"],
                    "context": {"category_description": category_data["description"]}
                }

            if tool_name not in category_data["tools"]:
                available_tools = list(category_data["tools"].keys())
                return {
                    "success": False,
                    "error": f"Unknown tool '{tool_name}' in category '{category}'",
                    "operation": "help",
                    "summary": f"Tool '{tool_name}' not found in category '{category}'",
                    "recovery_options": ["Choose from available tools in this category"],
                    "clarification_options": {
                        "tool_name": {
                            "description": f"What tool in {category} would you like help with?",
                            "options": available_tools
                        }
                    },
                    "context": {"available_tools": available_tools, "category": category}
                }

            # Return detailed help for specific tool
            tool_description = category_data["tools"][tool_name]
            detailed_help = {
                "tool": tool_name,
                "category": category,
                "description": tool_description,
                "usage_examples": [],
                "portmanteau_note": "This is a consolidated portmanteau tool with multiple operations"
            }

            # Add usage examples based on tool
            if tool_name == "file_ops":
                detailed_help["usage_examples"] = [
                    "file_ops('open', file_path='C:\\\\path\\\\to\\\\file.txt')",
                    "file_ops('new')",
                    "file_ops('save')",
                    "file_ops('info')"
                ]
                detailed_help["operations"] = ["open", "new", "save", "info"]
            elif tool_name == "text_ops":
                detailed_help["usage_examples"] = [
                    "text_ops('insert', text='Hello World')",
                    "text_ops('find', text='search term')"
                ]
                detailed_help["operations"] = ["insert", "find"]
            elif tool_name == "status_ops":
                detailed_help["usage_examples"] = [
                    "status_ops('help')",
                    "status_ops('system_status')",
                    "status_ops('health_check')"
                ]
                detailed_help["operations"] = ["help", "system_status", "health_check"]

            return {
                "success": True,
                "operation": "help",
                "summary": f"Detailed help for {tool_name}",
                "result": detailed_help,
                "next_steps": ["Try the usage examples", "Use the tool with specified operations"],
                "context": {"help_level": "detailed", "tool_type": "portmanteau"}
            }

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting help: {e}")
            return {
                "success": False,
                "error": f"Failed to get help information: {e}",
                "operation": "help",
                "summary": "Help system encountered an error",
                "recovery_options": ["Check Notepad++ is running", "Try again later"],
                "diagnostic_info": {"exception_type": type(e).__name__}
            }

    async def _handle_system_status(self) -> Dict[str, Any]:
        """Handle system status operation."""
        try:
            # This would need access to file_ops and controller
            # For now, return a placeholder
            return {
                "success": True,
                "operation": "system_status",
                "summary": "System status check completed",
                "result": {
                    "note": "Full system status requires integration with controller",
                    "timestamp": time.time()
                },
                "next_steps": ["Use health_check for system diagnostics"],
                "context": {"status_level": "basic"}
            }

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting system status: {e}")
            return {
                "success": False,
                "error": f"Failed to get system status: {e}",
                "operation": "system_status",
                "summary": "System status retrieval failed",
                "recovery_options": ["Check Notepad++ is running", "Verify system permissions"],
                "diagnostic_info": {"exception_type": type(e).__name__}
            }

    async def _handle_health_check(self) -> Dict[str, Any]:
        """Handle health check operation."""
        health_status = {
            "overall_status": "unknown",
            "checks": {},
            "recommendations": [],
            "timestamp": time.time(),
        }

        # Check 1: Windows API availability
        try:
            import win32api
            health_status["checks"]["windows_api"] = {
                "status": "pass",
                "message": "Windows API available",
            }
        except ImportError:
            health_status["checks"]["windows_api"] = {
                "status": "fail",
                "message": "Windows API not available",
            }
            return {
                "success": False,
                "error": "Windows API not available",
                "operation": "health_check",
                "summary": "Health check failed - Windows API unavailable",
                "result": health_status,
                "recovery_options": ["Install pywin32 package for Windows API access"],
                "context": {"critical_failure": True}
            }

        # Check 2: Notepad++ installation
        if self.controller:
            try:
                notepad_exe = self.controller._find_notepadpp_exe()
                health_status["checks"]["notepadpp_installation"] = {
                    "status": "pass",
                    "message": f"Notepad++ found at: {notepad_exe}",
                }
            except Exception as e:
                health_status["checks"]["notepadpp_installation"] = {
                    "status": "fail",
                    "message": f"Notepad++ not found: {e}",
                }
        else:
            health_status["checks"]["notepadpp_installation"] = {
                "status": "unknown",
                "message": "Controller not available",
            }

        # Check 3: System resources
        if PSUTIL_AVAILABLE:
            try:
                memory = psutil.virtual_memory()
                if memory.percent < 90:  # Less than 90% memory usage
                    health_status["checks"]["system_resources"] = {
                        "status": "pass",
                        "message": f"System resources OK (memory: {memory.percent:.1f}%)",
                    }
                else:
                    health_status["checks"]["system_resources"] = {
                        "status": "warn",
                        "message": f"High memory usage: {memory.percent:.1f}%",
                    }
            except Exception as e:
                health_status["checks"]["system_resources"] = {
                    "status": "warn",
                    "message": f"Could not check resources: {e}",
                }
        else:
            health_status["checks"]["system_resources"] = {
                "status": "unknown",
                "message": "psutil not available",
            }

        # Determine overall status
        check_statuses = [check["status"] for check in health_status["checks"].values()]
        if "fail" in check_statuses:
            overall_status = "fail"
        elif "warn" in check_statuses:
            overall_status = "warn"
        else:
            overall_status = "pass"

        health_status["overall_status"] = overall_status

        # Add general recommendations
        if overall_status == "pass":
            recommendations = ["All systems operational - no action required"]
        elif overall_status == "warn":
            recommendations = ["Monitor system for potential issues"]
        else:
            recommendations = ["Critical issues detected - address immediately"]

        health_status["recommendations"] = recommendations

        return {
            "success": True,
            "operation": "health_check",
            "summary": f"Health check completed - status: {overall_status}",
            "result": health_status,
            "next_steps": recommendations,
            "context": {"overall_status": overall_status, "checks_performed": len(health_status["checks"])}
        }