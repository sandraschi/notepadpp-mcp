# SOTA Gold Standard Docstring Template for Notepad++ MCP

## Template Structure

Every portmanteau tool docstring MUST follow this exact structure:

```python
@tool_decorator
async def tool_name(operation: Literal[...], param1: type, param2: type = default) -> Dict[str, Any]:
    """[Single line summary of tool purpose].

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating N separate tools (one per operation), this tool consolidates related
    operations into a single interface. Prevents tool explosion (N tools -> 1 tool) while maintaining
    full functionality and improving discoverability. Follows FastMCP 2.14.1+ SOTA standards.

    Supported Operations:
    - [High-level operation 1]
    - [High-level operation 2]
    - [High-level operation N]

    Operations Detail:
    **[Category 1]:**
    - "operation1": [What it does, when to use]
    - "operation2": [What it does, when to use]

    **[Category 2]:**
    - "operation3": [What it does, when to use]

    Prerequisites:
    - Windows OS with Notepad++ installed
    - pywin32 package for Windows API access
    - [Any other requirements]

    Args:
        operation (Literal, required): The operation to perform. Must be one of: "op1", "op2", "op3".
            - "op1": [Brief description, required params]
            - "op2": [Brief description, required params]
            - "op3": [Brief description, required params]

        param1 (str | None): [Parameter description]. Required for: [operations].
            [Additional context if needed]

        param2 (bool): [Parameter description]. Used by: [operations].
            Default: [default_value]. Valid values: [valid_values]

    Returns:
        **FastMCP 2.14.1+ Conversational Response Structure:**

        ```json
        {
          "success": true,
          "operation": "operation_name",
          "summary": "Conversational human-readable summary",
          "result": {
            // Operation-specific data
          },
          "next_steps": ["Suggested next actions"],
          "context": {
            "operation_details": "Additional context"
          },
          "suggestions": ["AI-friendly follow-up suggestions"],
          "follow_up_questions": ["Interactive questions for user"]
        }
        ```

        **Success Response Structure (Conversational):**
        - success (bool): Operation success status
        - operation (str): Operation that was performed
        - summary (str): Conversational description of what happened
        - result (dict): Operation-specific return data
        - next_steps (list[str]): Suggested actions user can take next
        - context (dict): Additional contextual information
        - suggestions (list[str]): AI-friendly follow-up suggestions
        - follow_up_questions (list[str]): Questions to engage user in dialogue

        **Error Recovery Response Structure (Conversational):**
        - success (bool): Always false for errors
        - error (str): Detailed, conversational error description
        - error_code (str): Machine-readable error code
        - message (str): Human-friendly explanation with context
        - recovery_options (list[str]): Step-by-step recovery instructions
        - diagnostic_info (dict): Technical details for debugging
        - alternative_solutions (list[str]): Alternative approaches
        - estimated_resolution_time (str): Time estimate for resolution
        - urgency (str): Priority level (low/medium/high)

        **Error Response Structure:**
        - success (bool): Always false for errors
        - error (str): Error type or code
        - operation (str): Failed operation
        - summary (str): Human-readable error summary
        - recovery_options (list[str]): Suggested recovery actions
        - clarification_options (dict): Parameter clarification if needed

    Examples:
        # Basic usage
        result = await tool_name("operation1", param1="value")
        # Returns: {"success": true, "summary": "Operation completed", ...}

        # Advanced usage with all parameters
        result = await tool_name("operation2", param1="value", param2=True)
        # Returns: {"success": true, "result": {...}, ...}

        # Error handling
        result = await tool_name("invalid_op")
        # Returns: {"success": false, "error": "Unknown operation", ...}

    Errors:
        **Common Errors:**
        - "Windows API not available": pywin32 not installed or Notepad++ not running
        - "Unknown operation": Invalid operation parameter
        - "Missing required parameter": Required parameter not provided for operation

        **Recovery Options:**
        - Install pywin32: `pip install pywin32`
        - Ensure Notepad++ is running
        - Check operation names against supported operations list
    """
```

## Implementation Notes

### Args Section Formatting (CRITICAL)
- **One parameter per line** - NO EXCEPTIONS
- **Explicit type hints**: `(str | None)`, `(list[str])`, `(Literal, required)`
- **Required/Optional context**: "Required for: X, Y operations" or "Used by: X operation"
- **Operation mapping**: Clearly state which operations use each parameter

### Portmanteau Rationale (MANDATORY)
Every consolidated tool must include the rationale block explaining why operations are grouped.

### Operations Detail (MANDATORY)
Break down operations by category with clear descriptions of what each does and when to use it.

### Examples (MANDATORY)
Provide minimal working code examples for:
- Basic usage
- Advanced usage with all parameters
- Error handling

### Error Documentation (MANDATORY)
Document common errors and recovery options in structured format.

## Validation Checklist

Before committing updated docstrings:

- [ ] PORTMANTEAU PATTERN RATIONALE included (2-3 lines max)
- [ ] Args section: one parameter per line, explicit types, operation context
- [ ] Operations Detail: categorized breakdown of all supported operations
- [ ] Examples: basic, advanced, error handling
- [ ] Returns: structured success/error response formats
- [ ] Errors: common errors with recovery options
- [ ] No duplication between sections
- [ ] All parameters documented
- [ ] Type hints match function signature

## Tool-Specific Notes

### file_operations.py
- Operations: open, new, save, info
- Categories: File Management (open, new, save), File Information (info)
- Prerequisites: File system access, Windows API

### text_operations.py
- Operations: insert, find
- Categories: Text Insertion (insert), Text Search (find)
- Prerequisites: Active document, Windows API

### status_operations.py
- Operations: help, system_status, health_check
- Categories: Help System (help), System Monitoring (system_status, health_check)
- Prerequisites: Windows API for health checks

### tab_operations.py
- Operations: list, switch, close
- Categories: Tab Management (list, switch, close)
- Prerequisites: Notepad++ running, open documents

### session_operations.py
- Operations: save, load, list
- Categories: Session Persistence (save, load, list)
- Prerequisites: File system access

### linting_operations.py
- Operations: python, javascript, json, markdown, tools
- Categories: Code Linting (python, javascript), Data Validation (json, markdown), Tool Info (tools)
- Prerequisites: External linters (ruff, eslint), file access

### display_operations.py
- Operations: fix_invisible_text, fix_display_issue
- Categories: Display Fixes (fix_invisible_text, fix_display_issue)
- Prerequisites: Notepad++ UI access

### plugin_operations.py
- Operations: discover, install, list, execute
- Categories: Plugin Discovery (discover, list), Plugin Management (install, execute)
- Prerequisites: Internet access for discovery, file system for installation