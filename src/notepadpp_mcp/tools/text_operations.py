"""
Text Operations Portmanteau Tool

Consolidates text operations (insert, find, write, replace_all, goto_line,
copy_selection, comment_uncomment, case, trim, line_ops, count) into one tool.

TRANSPORT: buffer text is read from disk for named files and via clipboard
round-trip for untitled buffers; writes use clipboard + keystrokes with
verify-after. Ops that need arbitrary character-range selection are not
supported on NPP 8.x (Scintilla SETSEL is not serviced externally).
"""

import re
from typing import Annotated, Any, Literal

from fastmcp import FastMCP
from pydantic import Field

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

_COMMENT_MAP = {
    ".py": "#",
    ".pyw": "#",
    ".ahk": ";",
    ".ahkl": ";",
}


def _comment_char_for(filename: str) -> str:
    """Pick a line-comment marker for the active filename (python #, ahk ;, else //)."""
    import os

    ext = os.path.splitext(filename or "")[1].lower()
    if ext in _COMMENT_MAP:
        return _COMMENT_MAP[ext]
    return "//"


def _toggle_comment(line: str, marker: str) -> str:
    stripped = line.lstrip()
    indent = line[: len(line) - len(stripped)]
    if stripped.startswith(marker):
        return indent + stripped[len(marker) :].lstrip()
    return indent + marker + " " + stripped


class TextOperationsTool:
    """Portmanteau tool for text operations in Notepad++."""

    def __init__(self, app: FastMCP, controller=None):
        """Initialize the text operations tool."""
        self.app = app
        self.controller = controller

    def register_tools(self):
        """Register text operations portmanteau tool."""

        @self.app.tool()
        async def text_ops(
            operation: Annotated[
                Literal[
                    "insert",
                    "find",
                    "write",
                    "replace_all",
                    "goto_line",
                    "copy_selection",
                    "comment_uncomment",
                    "case",
                    "trim",
                    "line_ops",
                    "count",
                ],
                Field(
                    description=(
                        "Operation: insert writes text at the caret; find searches the buffer; "
                        "write replaces the WHOLE buffer (refuses on a non-empty named file unless force=true); "
                        "replace_all swaps all occurrences of text with replacement; goto_line moves the caret; "
                        "copy_selection returns the currently selected text; "
                        "comment_uncomment toggles line comments; case converts case; trim removes whitespace; "
                        "line_ops sorts/joins/duplicates lines; count reports stats and occurrences."
                    )
                ),
            ],
            text: Annotated[
                str | None,
                Field(
                    description="Primary text: to insert/find, the search pattern for replace_all/find, or the search term for count."
                ),
            ] = None,
            replacement: Annotated[
                str | None,
                Field(description="Replacement text for replace_all (required for replace_all)."),
            ] = None,
            case_sensitive: Annotated[
                bool, Field(description="Case-sensitive matching for find/replace_all (default False).")
            ] = False,
            regex: Annotated[
                bool, Field(description="Treat text as a regular expression for replace_all (default False).")
            ] = False,
            edit_ok: Annotated[
                bool,
                Field(
                    description="Allow insert into a non-empty named file (default False; use file_ops new for generation tasks)."
                ),
            ] = False,
            force: Annotated[
                bool, Field(description="Allow write to overwrite a non-empty buffer (default False).")
            ] = False,
            line: Annotated[int | None, Field(description="1-based line number for goto_line.")] = None,
            mode: Annotated[
                str | None,
                Field(
                    description=(
                        "Variant: case: upper|lower|title; trim: all|leading|trailing; "
                        "line_ops: sort|join|duplicate; comment_uncomment: auto|python|js (default auto)."
                    )
                ),
            ] = None,
            reverse: Annotated[bool, Field(description="Sort descending for line_ops sort (default False).")] = False,
        ) -> dict[str, Any]:
            """TEXT_OPS — Insert, find, write, replace, navigate, and transform the active buffer.

            PORTMANTEAU PATTERN RATIONALE: Single tool for all buffer text operations per
            TOOL_DESIGN_STANDARDS.md §1.

            Safety: `write` replaces the WHOLE buffer and refuses when the active tab is a
            non-empty named file unless force=true - for generation tasks, create a fresh
            tab first with file_ops(operation="new"). Transforms are verified after the
            write; a failed verification returns success=False instead of lying.

            Operations:
            - insert: Insert `text` at the caret (requires edit_ok=true when the active buffer is a non-empty named file).
            - find: Search for `text`; use case_sensitive for matching.
            - write: Replace the entire buffer (guarded - see above).
            - replace_all: Replace all occurrences of `text` with `replacement` (regex supported).
            - goto_line: Move the caret to `line` (1-based).
            - copy_selection: Return the currently selected text.
            - comment_uncomment: Toggle line comments (mode auto detects python # vs //; whole buffer).
            - case: Convert case (mode upper|lower|title; whole buffer).
            - trim: Strip whitespace (mode all|leading|trailing; whole buffer).
            - line_ops: mode sort (reverse flag), join, or duplicate lines (whole buffer).
            - count: Report chars/words/lines and optionally occurrences of `text`.

            ## Return Format
            {"success": bool, "operation": str, "message": str, "result": {...}, "error": str | null}

            ## Examples
            text_ops(operation="insert", text="hello")
            text_ops(operation="find", text="TODO", case_sensitive=False)
            text_ops(operation="write", text="Roses are red")
            text_ops(operation="replace_all", text="old", replacement="new", case_sensitive=True)
            text_ops(operation="goto_line", line=42)
            text_ops(operation="case", mode="upper")
            text_ops(operation="trim", mode="all")
            text_ops(operation="line_ops", mode="sort", reverse=True)
            text_ops(operation="count", text="TODO")

            Notes:
             - Missing text, no active document, or Windows API unavailable returns success=False with recovery_options.
             - write/insert guards return success=False with recovery options instead of touching a guarded buffer.
             - Text transport needs the editor to come to the foreground; if that fails (e.g. locked session),
               operations return success=False with a clear reason rather than faking success.
            """
            if not self.controller:
                return {
                    "success": False,
                    "error": "Windows API not available",
                    "operation": operation,
                    "summary": "Text operation failed - Windows API unavailable",
                    "recovery_options": [
                        "Ensure pywin32 is installed",
                        "Restart the MCP server",
                    ],
                }

            try:
                await self.controller.ensure_notepadpp_running()

                state = self.controller.get_active_tab_state()

                if operation == "insert":
                    if not text:
                        return _missing_text(operation)
                    buffer_len = self.controller.get_buffer_length()
                    if buffer_len > 0 and not (state["untitled"] or edit_ok):
                        return {
                            "success": False,
                            "error": "insert_refused",
                            "operation": operation,
                            "summary": "Insert refused: the active tab is a non-empty named file",
                            "message": (
                                f"The active tab holds '{state['filename']}' with content. "
                                "To edit this file, pass edit_ok=true. For generation tasks, "
                                "open a fresh tab first with file_ops(operation='new')."
                            ),
                            "recovery_options": [
                                "file_ops(operation='new') then text_ops(operation='insert', ...)",
                                "text_ops(operation='insert', text=..., edit_ok=true) to edit the active file",
                            ],
                            "context": state,
                        }
                    if not self.controller.insert_at_caret(text):
                        return {
                            "success": False,
                            "error": "foreground_unavailable",
                            "operation": operation,
                            "summary": "Could not bring the editor to the foreground - insert aborted",
                            "recovery_options": [
                                "Bring Notepad++ to the foreground and retry",
                                "Run the MCP client from your interactive desktop session",
                            ],
                        }
                    # Verify: the caret insertion should be present in the LIVE buffer.
                    live = self.controller.get_live_buffer_text().replace("\r\n", "\n").replace("\r", "\n")
                    if text not in live:
                        return {
                            "success": False,
                            "error": "verification_failed",
                            "operation": operation,
                            "summary": "Insert ran but the buffer does not contain the text - no change made",
                            "recovery_options": ["Retry once", "Check the active tab is the one you expect"],
                            "context": state,
                        }
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Successfully inserted {len(text)} characters",
                        "result": {"inserted_chars": len(text), "target_tab": state},
                        "next_steps": ["Use file_ops save to save changes", "Use text_ops find to locate content"],
                        "context": {"tab": state},
                    }

                elif operation == "find":
                    if not text:
                        return _missing_text(operation)
                    full, _source = self.controller.get_buffer_text()
                    flags = 0 if case_sensitive else re.IGNORECASE
                    matches = [(m.start(), m.end()) for m in re.finditer(re.escape(text), full, flags)]
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Found {len(matches)} occurrence(s) of '{text}'",
                        "result": {
                            "count": len(matches),
                            "positions": matches[:50],
                            "total_matches": len(matches),
                            "source": _source,
                        },
                        "next_steps": [
                            "Use text_ops goto_line to jump to a match",
                            "Use text_ops replace_all to replace them",
                        ],
                        "context": {"case_sensitive": case_sensitive, "tab": state},
                    }

                elif operation == "write":
                    if text is None:
                        return _missing_text(operation)
                    buffer_len = self.controller.get_buffer_length()
                    if buffer_len > 0 and not (state["untitled"] or force):
                        return {
                            "success": False,
                            "error": "write_refused",
                            "operation": operation,
                            "summary": "Write refused: the active tab is a non-empty named file",
                            "message": (
                                f"Refusing to overwrite '{state['filename']}' ({buffer_len} chars). "
                                "For generation tasks open a fresh tab first: file_ops(operation='new'). "
                                "Pass force=true only to explicitly replace the active buffer."
                            ),
                            "recovery_options": [
                                "file_ops(operation='new') then text_ops(operation='write', text=...)",
                                "text_ops(operation='write', text=..., force=true) to overwrite explicitly",
                            ],
                            "context": {**state, "buffer_length": buffer_len},
                        }
                    if not self.controller.set_buffer_text(text):
                        return {
                            "success": False,
                            "error": "foreground_unavailable",
                            "operation": operation,
                            "summary": "Could not bring the editor to the foreground - write aborted",
                            "recovery_options": [
                                "Bring Notepad++ to the foreground and retry",
                                "Run the MCP client from your interactive desktop session",
                            ],
                        }
                    if not self.controller.verify_buffer(text):
                        return {
                            "success": False,
                            "error": "verification_failed",
                            "operation": operation,
                            "summary": "Write ran but verification failed - the buffer does not match the requested text",
                            "recovery_options": ["Retry once", "Use file_ops is_dirty to inspect the tab state"],
                        }
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Wrote {len(text)} characters to the buffer (verified)",
                        "result": {"written_chars": len(text), "target_tab": state, "verified": True},
                        "next_steps": ["Use file_ops save (or save_as) to persist", "Use text_ops count to verify"],
                    }

                elif operation == "replace_all":
                    if not text or replacement is None:
                        return {
                            "success": False,
                            "error": "missing_parameters",
                            "operation": operation,
                            "summary": "replace_all requires both text and replacement",
                            "recovery_options": ["Provide text (pattern) and replacement"],
                        }
                    full, _source = self.controller.get_buffer_text()
                    if regex:
                        flags = 0 if case_sensitive else re.IGNORECASE
                        try:
                            new_text, count = re.subn(text, replacement, full, flags=flags)
                        except re.error as e:
                            return {
                                "success": False,
                                "error": "invalid_regex",
                                "operation": operation,
                                "summary": f"Invalid regular expression: {e}",
                            }
                    else:
                        if case_sensitive:
                            count = full.count(text)
                            new_text = full.replace(text, replacement)
                        else:
                            pattern = re.compile(re.escape(text), re.IGNORECASE)
                            new_text, count = pattern.subn(lambda m: replacement, full)
                    if count == 0:
                        return {
                            "success": True,
                            "operation": operation,
                            "summary": "No occurrences found - nothing to replace",
                            "result": {"replacements": 0, "changed": False},
                        }
                    if not self.controller.set_buffer_text(new_text):
                        return {
                            "success": False,
                            "error": "foreground_unavailable",
                            "operation": operation,
                            "summary": "Could not bring the editor to the foreground - replace aborted",
                            "recovery_options": ["Bring Notepad++ to the foreground and retry"],
                        }
                    if not self.controller.verify_buffer(new_text):
                        return {
                            "success": False,
                            "error": "verification_failed",
                            "operation": operation,
                            "summary": "Replace ran but verification failed",
                            "recovery_options": ["Retry once"],
                        }
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Replaced {count} occurrence(s) (verified)",
                        "result": {"replacements": count, "changed": True, "verified": True},
                        "next_steps": ["Use file_ops save to persist", "Use text_ops find to verify"],
                        "context": {"regex": regex, "case_sensitive": case_sensitive},
                    }

                elif operation == "goto_line":
                    if line is None or line < 1:
                        return {
                            "success": False,
                            "error": "invalid_line",
                            "operation": operation,
                            "summary": "goto_line requires a positive 1-based line number",
                            "recovery_options": ["Provide line >= 1"],
                        }
                    self.controller.goto_line(line)
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Moved caret to line {line}",
                        "result": {
                            "line": line,
                            "line_count": self.controller.get_line_count(),
                            "caret": self.controller.get_caret(),
                        },
                    }

                elif operation == "copy_selection":
                    if not self.controller.copy_selection_to_clipboard():
                        return {
                            "success": False,
                            "error": "foreground_unavailable",
                            "operation": operation,
                            "summary": "Could not bring the editor to the foreground - copy aborted",
                            "recovery_options": ["Bring Notepad++ to the foreground and retry"],
                        }
                    selected = self.controller._clipboard_get()
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Copied {len(selected)} selected characters",
                        "result": {"selection": selected, "selection_length": len(selected)},
                        "next_steps": ["Use text_ops insert to paste it elsewhere", "Use text_ops count for stats"],
                    }

                elif operation == "comment_uncomment":
                    full, _source = self.controller.get_buffer_text()
                    marker = _comment_char_for(state["filename"])
                    if mode in ("python", "js"):
                        marker = "#" if mode == "python" else "//"
                    lines = full.split("\n")
                    changed = 0
                    for i, ln in enumerate(lines):
                        toggled = _toggle_comment(ln, marker)
                        if toggled != ln:
                            changed += 1
                            lines[i] = toggled
                    if changed == 0:
                        return {
                            "success": True,
                            "operation": operation,
                            "summary": "No lines to toggle",
                            "result": {"changed_lines": 0, "marker": marker},
                        }
                    new_text = "\n".join(lines)
                    if not self.controller.set_buffer_text(new_text) or not self.controller.verify_buffer(new_text):
                        return {
                            "success": False,
                            "error": "verification_failed",
                            "operation": operation,
                            "summary": "Comment toggle could not be applied",
                            "recovery_options": ["Retry once", "Bring Notepad++ to the foreground"],
                        }
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Toggled comments on {changed} line(s) using '{marker}' (verified)",
                        "result": {"changed_lines": changed, "marker": marker, "verified": True},
                    }

                elif operation == "case":
                    full, _source = self.controller.get_buffer_text()
                    if mode == "upper":
                        new_text = full.upper()
                    elif mode == "lower":
                        new_text = full.lower()
                    else:
                        new_text = full.title()
                    if not self.controller.set_buffer_text(new_text) or not self.controller.verify_buffer(new_text):
                        return {
                            "success": False,
                            "error": "verification_failed",
                            "operation": operation,
                            "summary": "Case conversion could not be applied",
                            "recovery_options": ["Retry once", "Bring Notepad++ to the foreground"],
                        }
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Converted case ({mode or 'title'}) - verified",
                        "result": {"mode": mode or "title", "verified": True},
                    }

                elif operation == "trim":
                    full, _source = self.controller.get_buffer_text()
                    trim_mode = mode or "all"
                    if trim_mode == "leading":
                        new_text = "\n".join(ln.lstrip() for ln in full.split("\n"))
                    elif trim_mode == "trailing":
                        new_text = "\n".join(ln.rstrip() for ln in full.split("\n"))
                    else:
                        new_text = "\n".join(ln.strip() for ln in full.split("\n"))
                    if not self.controller.set_buffer_text(new_text) or not self.controller.verify_buffer(new_text):
                        return {
                            "success": False,
                            "error": "verification_failed",
                            "operation": operation,
                            "summary": "Trim could not be applied",
                            "recovery_options": ["Retry once", "Bring Notepad++ to the foreground"],
                        }
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Trimmed whitespace ({trim_mode}) - verified",
                        "result": {"mode": trim_mode, "verified": True},
                    }

                elif operation == "line_ops":
                    full, _source = self.controller.get_buffer_text()
                    lines = full.split("\n")
                    line_mode = mode or "sort"
                    if line_mode == "sort":
                        lines = sorted(lines, reverse=reverse)
                    elif line_mode == "join":
                        lines = [" ".join(part.strip() for part in lines if part.strip())]
                    elif line_mode == "duplicate":
                        lines = [ln for ln in lines for _ in range(2)]
                    else:
                        return {
                            "success": False,
                            "error": "invalid_mode",
                            "operation": operation,
                            "summary": "line_ops mode must be sort, join, or duplicate",
                            "recovery_options": ["Use mode='sort' | 'join' | 'duplicate'"],
                        }
                    new_text = "\n".join(lines)
                    if not self.controller.set_buffer_text(new_text) or not self.controller.verify_buffer(new_text):
                        return {
                            "success": False,
                            "error": "verification_failed",
                            "operation": operation,
                            "summary": "Line operation could not be applied",
                            "recovery_options": ["Retry once", "Bring Notepad++ to the foreground"],
                        }
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Line operation '{line_mode}' applied - verified",
                        "result": {"mode": line_mode, "reverse": reverse, "verified": True},
                    }

                elif operation == "count":
                    full, _source = self.controller.get_buffer_text()
                    words = len(full.split()) if full.strip() else 0
                    occurrences = 0
                    if text:
                        flags = 0 if case_sensitive else re.IGNORECASE
                        occurrences = len(re.findall(re.escape(text), full, flags))
                    return {
                        "success": True,
                        "operation": operation,
                        "summary": f"Buffer stats: {len(full)} chars, {words} words, {full.count(chr(10)) + 1} lines"
                        + (f", {occurrences} occurrence(s) of '{text}'" if text else ""),
                        "result": {
                            "chars": len(full),
                            "words": words,
                            "lines": full.count("\n") + 1 if full else 0,
                            "occurrences": occurrences,
                            "source": _source,
                        },
                        "context": {"search_text": text, "case_sensitive": case_sensitive},
                    }

                else:
                    return {
                        "success": False,
                        "error": f"Unknown operation: {operation}",
                        "operation": operation,
                        "summary": f"Text operation failed - unknown operation '{operation}'",
                        "recovery_options": [
                            "Use 'insert', 'find', 'write', 'replace_all', 'goto_line', "
                            "'copy_selection', 'comment_uncomment', 'case', 'trim', 'line_ops', or 'count'"
                        ],
                    }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Text operation failed: {e}",
                    "operation": operation,
                    "summary": f"Text operation '{operation}' encountered an error",
                    "recovery_options": [
                        "Check Notepad++ is running",
                        "Verify text content",
                        "Restart Notepad++",
                    ],
                    "diagnostic_info": {
                        "exception_type": type(e).__name__,
                        "operation": operation,
                        "text_length": len(text) if text else 0,
                    },
                }


def _missing_text(operation: str) -> dict[str, Any]:
    """Standard error for operations that require text."""
    return {
        "success": False,
        "error": "text parameter required",
        "operation": operation,
        "summary": "Text operation failed - missing text parameter",
        "clarification_options": {"text": {"description": "What text would you like to use?", "type": "text_input"}},
    }
