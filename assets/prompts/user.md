# Notepad++ MCP Server - User Interaction Guide

## GETTING STARTED WITH NOTEPAD++ AUTOMATION

Welcome to the Notepad++ MCP Server! This comprehensive automation system allows you to control Notepad++ through natural language commands. Whether you're editing code, managing multiple files, or performing code quality analysis, the server provides seamless integration with Claude Desktop.

### FIRST STEPS

**Basic File Operations**
"Open a new file in Notepad++"
→ Server creates new file and confirms: "New file created successfully. Ready for content."

"Save the current file as 'my_script.py'"
→ Server saves file and responds: "File saved as my_script.py"

"Show me information about the current file"
→ Server provides: "Current file: my_script.py, Size: 1.2KB, Modified: just now"

**Understanding the Response Format**
Every operation returns structured feedback:
- **Success status**: Whether the operation completed
- **Summary**: What was accomplished
- **Next steps**: Suggested follow-up actions
- **Context**: Technical details about the operation

### CORE WORKFLOW PATTERNS

#### PATTERN 1: CODE DEVELOPMENT WORKFLOW
"I need to create a Python script for data analysis"
1. Server: Creates new file
2. "Add the basic imports: import pandas as pd, import numpy as np"
3. Server: Inserts import statements
4. "Check the code quality"
5. Server: Runs Python linting, suggests improvements
6. "Save as data_processor.py"
7. Server: Saves file with proper extension

#### PATTERN 2: MULTI-FILE PROJECT MANAGEMENT
"I want to work on my web project with HTML, CSS, and JavaScript files"
1. Server: Opens all three files in separate tabs
2. "Switch to the CSS file"
3. Server: Changes active tab to CSS file
4. "Add responsive design styles"
5. Server: Inserts CSS content
6. "Check all files for syntax errors"
7. Server: Lints each file type appropriately
8. "Save my current workspace as 'web_project_session'"
9. Server: Preserves all open files and cursor positions

#### PATTERN 3: CODE REVIEW AND QUALITY ASSURANCE
"I need to review this JavaScript file for issues"
1. Server: Opens and displays file content
2. "Run JavaScript linting on this file"
3. Server: Analyzes code, reports errors and warnings
4. "Fix the undefined variable error"
5. Server: Suggests correction or applies automatic fix
6. "Check if there are any other issues"
7. Server: Re-runs analysis, confirms fixes

## DETAILED TOOL USAGE EXAMPLES

### FILE OPERATIONS (file_ops)

**Creating and Opening Files**
"Create a new text file"
→ Creates new untitled file in Notepad++

"Open my todo.txt file from the desktop"
→ Locates and opens C:\Users\username\Desktop\todo.txt

"Start a new Python script"
→ Creates new file, suggests .py extension

**Saving and Managing Files**
"Save this file as config.json"
→ Saves current file with JSON extension

"Save all changes"
→ Commits current file to disk

"What's the current file's status?"
→ Shows file path, size, modification time, encoding

**Error Handling Examples**
"Open /nonexistent/path/file.txt"
→ Returns: "File not found. Check path exists. Try: Verify file location, use absolute path"

### TEXT OPERATIONS (text_ops)

**Content Insertion**
"Add 'Hello World' at the top of the file"
→ Inserts text at beginning

"Insert this function at line 10:
def calculate_average(numbers):
    return sum(numbers) / len(numbers)"
→ Adds code block at specified location

"Add copyright notice to the header"
→ Inserts standard copyright text

**Text Search and Navigation**
"Find the word 'TODO' in the file"
→ Highlights all occurrences, shows line numbers

"Search for 'function' case-sensitive"
→ Finds exact case matches only

"Find the next occurrence of 'error'"
→ Moves cursor to next instance

**Advanced Text Operations**
"Replace all 'var' with 'const' in JavaScript"
→ Performs bulk replacement with confirmation

"Insert markdown table template"
→ Adds formatted table structure

### TAB MANAGEMENT (tab_ops)

**Multi-File Workflows**
"Show me all open tabs"
→ Lists: "Tab 1: script.py, Tab 2: README.md, Tab 3: config.json"

"Switch to the second tab"
→ Changes active file to README.md

"Close the config.json tab"
→ Closes specific tab, switches to adjacent tab

**Tab Organization**
"Which tab is currently active?"
→ Returns: "Active: script.py (Tab 2)"

"Close all tabs except the current one"
→ Keeps current file open, closes others

### SESSION MANAGEMENT (session_ops)

**Workspace Preservation**
"Save my current workspace as 'morning_work'"
→ Saves all open files, cursor positions, active tab

"Show me my saved sessions"
→ Lists: "morning_work (3 files), afternoon_coding (5 files)"

"Restore my morning work session"
→ Reopens all files, restores exact cursor positions

**Session Organization**
"Rename the current session to 'project_v2'"
→ Updates session name in storage

"Delete the old backup session"
→ Removes unwanted session data

### CODE QUALITY ANALYSIS (linting_ops)

**Python Code Review**
"Check this Python file for issues"
→ Analyzes with multiple tools, reports:
- Syntax errors
- Style violations (PEP8)
- Unused imports
- Complexity issues
- Type hints suggestions

**JavaScript Validation**
"Validate my JavaScript code"
→ Checks for:
- Syntax errors
- Undefined variables
- Code style issues
- Potential bugs

**JSON and Markdown Quality**
"Verify this JSON configuration"
→ Validates structure, reports formatting issues

"Check markdown formatting"
→ Reviews headers, links, code blocks, lists

**Comprehensive Analysis**
"Run full code quality check on all files"
→ Lints each file type appropriately, provides summary report

### DISPLAY AND VISUAL FIXES (display_ops)

**Common Display Issues**
"The text is invisible in Notepad++"
→ Resets theme colors, fixes white-on-white text

"Notepad++ looks corrupted"
→ Restores default display settings, clears visual glitches

**Theme and Appearance**
"Fix the display problem"
→ Resets all visual settings to defaults

### PLUGIN ECOSYSTEM (plugin_ops)

**Plugin Discovery**
"Find plugins for code analysis"
→ Searches 1,400+ plugins, returns relevant matches

"Show me plugins for version control"
→ Lists Git, SVN, and other VCS plugins

**Plugin Installation**
"Install the XML Tools plugin"
→ Downloads and installs from official repository

"Add the Compare plugin"
→ Installs file comparison tool

**Plugin Usage**
"Use the installed JSON Viewer on this file"
→ Executes plugin command on current file

"Run the HTML Tidy plugin"
→ Formats HTML with official plugin

## ADVANCED USAGE SCENARIOS

### DEVELOPMENT WORKFLOW AUTOMATION

**Scenario: New Feature Development**
1. "Create a new feature branch workflow script"
2. Server creates Python file with template
3. "Add git branch creation logic"
4. Server inserts branching code
5. "Include error handling for merge conflicts"
6. Server adds try-catch blocks
7. "Check the code quality"
8. Server runs linting, suggests improvements
9. "Save as git_workflow.py"
10. Server saves with proper naming

**Scenario: Web Development Setup**
1. "Set up a new web project structure"
2. Server creates HTML, CSS, JS files
3. "Add responsive HTML5 template"
4. Server inserts modern HTML structure
5. "Create CSS reset and grid system"
6. Server adds comprehensive CSS framework
7. "Add JavaScript utility functions"
8. Server inserts common JS helpers
9. "Validate all code"
10. Server lints each file type
11. "Save the project workspace"
12. Server preserves all files

### DEBUGGING AND TROUBLESHOOTING

**Scenario: Code Issue Resolution**
1. "Open the buggy script.py"
2. Server opens file
3. "Run Python linting to find issues"
4. Server identifies syntax errors, unused variables
5. "Fix the indentation error on line 25"
6. Server corrects indentation
7. "Add missing import for os module"
8. Server inserts import statement
9. "Verify the fixes work"
10. Server re-lints, confirms resolution

**Scenario: System Integration Issues**
1. "Check if Notepad++ is running properly"
2. Server verifies process status
3. "Test file operations work"
4. Server attempts basic file operations
5. "Diagnose any connection problems"
6. Server provides detailed system status
7. "Fix any display issues found"
8. Server resets visual settings

### PRODUCTIVITY ENHANCEMENT

**Scenario: Daily Development Routine**
1. "Load yesterday's work session"
2. Server restores all files and positions
3. "Review today's TODO list"
4. Server opens task file
5. "Start working on the first task"
6. Server opens relevant project files
7. "Check code quality periodically"
8. Server provides ongoing quality metrics
9. "Save progress throughout the day"
10. Server maintains workspace state

**Scenario: Code Review Preparation**
1. "Open all Python files in the project"
2. Server opens multiple files in tabs
3. "Run comprehensive linting on all files"
4. Server analyzes entire codebase
5. "Generate a quality report"
6. Server summarizes all issues found
7. "Create fixes for critical issues"
8. Server applies automated corrections
9. "Save the improved code"
10. Server commits all changes

## CONFIGURATION AND CUSTOMIZATION

### Basic Configuration
"Set Notepad++ path to custom location"
→ Updates configuration for non-standard installation

"Enable auto-start for Notepad++"
→ Server will launch Notepad++ if not running

"Set operation timeout to 60 seconds"
→ Increases timeout for slow operations

### Advanced Settings
"Configure for high-performance mode"
→ Optimizes settings for faster operations

"Set up logging for debugging"
→ Enables detailed operation logging

## ERROR RECOVERY PATTERNS

### File Operation Errors
**"File not found" responses:**
- "Try using the full absolute path"
- "Check if the file exists in File Explorer"
- "Verify file permissions and access rights"

**"Permission denied" responses:**
- "Run as administrator if needed"
- "Check if file is locked by another program"
- "Close conflicting applications"

### System Integration Errors
**"Notepad++ not running" responses:**
- "Launch Notepad++ manually"
- "Check installation integrity"
- "Verify Windows API accessibility"

**"Operation timeout" responses:**
- "Increase timeout setting"
- "Check system performance"
- "Close unnecessary applications"

### Plugin Operation Errors
**"Plugin installation failed" responses:**
- "Verify internet connection"
- "Check administrator privileges"
- "Confirm plugin compatibility"

**"Plugin execution error" responses:**
- "Check plugin documentation"
- "Verify command parameters"
- "Update plugin to latest version"

## PERFORMANCE OPTIMIZATION

### Efficient Workflows
"Use session management for complex projects"
→ Preserves state, reduces setup time

"Batch file operations when possible"
→ Minimizes individual operation overhead

"Use appropriate linting scope"
→ Target specific files rather than entire projects for frequent checks

### Resource Management
"Close unnecessary tabs regularly"
→ Reduces memory usage

"Save sessions before complex operations"
→ Preserves work if operations fail

"Monitor system status during intensive tasks"
→ Tracks performance and identifies bottlenecks

## INTEGRATION WITH CLAUDE DESKTOP

### Conversational Patterns
**Natural Language Commands:**
- "I need to edit a config file" → Server opens file creation dialog
- "Show me the current project structure" → Server displays open files overview
- "Fix the code issues" → Server applies linting and corrections
- "Save my work" → Server commits all changes

**Context-Aware Responses:**
- Server remembers recent operations
- Suggests logical next steps
- Provides operation history
- Offers alternative approaches

### Progressive Enhancement
**Basic to Advanced Usage:**
1. **Beginner**: Simple file operations
2. **Intermediate**: Multi-file workflows, basic linting
3. **Advanced**: Session management, plugin integration, complex automation
4. **Expert**: Custom configurations, performance optimization, system integration

## TROUBLESHOOTING GUIDE

### Common Issues and Solutions

**Issue: "Server not responding"**
- Check if Notepad++ is running
- Verify Claude Desktop connection
- Restart both applications
- Check system resources

**Issue: "File operations failing"**
- Use absolute paths
- Check file permissions
- Close conflicting applications
- Verify file system accessibility

**Issue: "Plugin installation issues"**
- Ensure internet connection
- Run with administrator privileges
- Check plugin compatibility
- Verify Notepad++ version

**Issue: "Display problems"**
- Use display fix operations
- Restart Notepad++
- Reset to default theme
- Update graphics drivers

### Diagnostic Procedures

**System Health Check:**
1. Run status_ops("system_status")
2. Verify Notepad++ installation
3. Check Windows API access
4. Validate file system permissions

**Operation Validation:**
1. Test basic file operations
2. Verify text manipulation works
3. Check tab navigation
4. Validate plugin system

**Performance Monitoring:**
1. Monitor operation timing
2. Track resource usage
3. Identify bottlenecks
4. Optimize workflows

## EXTENDED EXAMPLES LIBRARY

### Code Development Examples

**Python Data Processing Script:**
1. Create new file
2. Add data processing imports
3. Insert main processing logic
4. Add error handling
5. Run linting and fix issues
6. Save as data_processor.py

**JavaScript Web Component:**
1. Create HTML, CSS, JS files
2. Add component structure
3. Implement functionality
4. Add event handlers
5. Test and validate code
6. Save component files

**JSON Configuration Management:**
1. Create structured JSON file
2. Add configuration sections
3. Validate JSON syntax
4. Add comments and documentation
5. Save configuration file

### Documentation and Content Creation

**Markdown Technical Documentation:**
1. Create README.md structure
2. Add installation instructions
3. Include usage examples
4. Add troubleshooting section
5. Validate markdown formatting
6. Save documentation

**Code Documentation Generation:**
1. Analyze Python/JavaScript files
2. Extract function signatures
3. Generate documentation templates
4. Add usage examples
5. Validate documentation format

### System Administration Tasks

**Configuration File Management:**
1. Open system configuration files
2. Update settings as needed
3. Validate configuration syntax
4. Create backup copies
5. Apply configuration changes

**Log File Analysis:**
1. Open log files
2. Search for specific patterns
3. Extract error information
4. Generate analysis reports
5. Archive processed logs

This comprehensive guide covers the full spectrum of Notepad++ MCP Server capabilities, from basic file operations to advanced automation workflows. The server provides natural language control over Notepad++ while maintaining professional-grade reliability and performance.

## DAILY WORKFLOW WALKTHROUGHS

### Morning: Resume Yesterday's Workspace

1. "Check that Notepad++ is running" - the server verifies reachability.
2. "Show my saved sessions" - list persisted workspaces.
3. "Load the session called 'yesterday'" - restores all open buffers.
4. "Show the active file info" - confirms the editor is in the expected state.

Why this matters: sessions are the safety net for long-running projects. Getting into the habit of saving a session before closing Notepad++ means you can always return to the same buffer set the next morning, even after a restart.

### Mid-Day: Edit and Verify Code

1. "Open src/parser.py" - loads the target file.
2. "Find the function called parse_line" - locates the edit point.
3. "Insert a docstring above it" - applies the change at the caret.
4. "Save the file" - persists the edit.
5. "Lint the python file src/parser.py" - runs ruff or the fallback checker.
6. "Show me the issues" - review severity, line, and column, then fix each with text_ops.

The verify loop is the core discipline: edit, save, lint, fix, re-lint. Never declare work finished on an un-linted file when the server exposes linting tools.

### Afternoon: Multi-File Refactor

1. "List my tabs" - see which files are open and their indices.
2. "Switch to tab 2" - move to the next file.
3. "Find 'TODO' in this file" - locate pending work.
4. "Switch to tab 4" - continue through the workspace.
5. "Save my workspace as 'refactor-2026'" - snapshot the state before risky edits.
6. "Install the plugin Compare" - pull in a diff tool from the official catalog.
7. "Execute Compare" - run the newly installed plugin command.

Multi-file work is where tab_ops and session_ops earn their keep. Snapshot before, not after: a session saved after a mistake preserves the mistake.

### Evening: Close Out Cleanly

1. "Lint the python file in the active tab" - final quality gate.
2. "Save my workspace as 'end-of-day'" - persist the state.
3. "Check the theme status" - optional: switch to dark mode for late-night work.
4. "Fix the invisible text" - recover from rendering glitches seen during the day.

## WORKING WITH THE RESPONSE FORMAT

Every tool response is structured. Read it like a receipt:

- success: true means the operation completed; read the summary for what changed.
- success: false means the operation did NOT complete; read the error and recovery options.
- next_steps and suggestions tell you what to do next; follow them or ask the user.
- diagnostic_info is technical context you can use to decide whether a retry makes sense.

If a tool fails, do not silently retry. Read the error, apply the recovery option, and only then retry. If the error is a missing parameter, ask the user for the value directly.

## COMMON TASKS AND THE EXACT TOOL CALLS

| Task | Tool call |
|------|-----------|
| Open a file | file_ops(operation="open", file_path="C:/...") |
| Insert text | text_ops(operation="insert", text="...") |
| Find text | text_ops(operation="find", text="...", case_sensitive=False) |
| List tabs | tab_ops(operation="list") |
| Switch tab | tab_ops(operation="switch", tab_index=2) |
| Close tab | tab_ops(operation="close", tab_index=2) |
| Save session | session_ops(operation="save", session_name="name") |
| Load session | session_ops(operation="load", session_name="name") |
| Lint python | linting_ops(operation="python", file_path="C:/...") |
| Check theme | display_ops(operation="theme_status") |
| Set dark mode | display_ops(operation="set_dark_mode", dark_mode=True) |
| Find plugin | plugin_ops(operation="discover", search_term="xml") |
| Install plugin | plugin_ops(operation="install", plugin_name="XMLTools") |
| Health check | status_ops(operation="health_check") |
| Server status | status_ops(operation="system_status") |

## FREQUENTLY ASKED QUESTIONS

**Q: The server says Windows API unavailable. What now?**
A: The server runs on Windows and needs pywin32. Re-run `uv sync` on the Windows machine and restart the server. If you are on another OS, Notepad++ automation is not supported.

**Q: Notepad++ is not detected even though it is running.**
A: Set NOTEPADPP_PATH to the exact path of notepad++.exe, or check the health_check output for the discovery failure reason.

**Q: The chat page says no local LLM is detected.**
A: Start Ollama (or LM Studio) and verify the Settings page shows a detected provider. The chat router uses AI_ENDPOINT and AI_MODEL from the environment.

**Q: Can the server open files outside my projects?**
A: It can open any path the OS lets the server process access. Use absolute paths when in doubt.

**Q: Plugin install does nothing.**
A: Install uses UI automation toward the Plugin Admin dialog. Run it once, watch the dialog, and do not start parallel installs. If the catalog is unreachable, set NOTEPADPP_PLUGIN_LIST_URL to a mirror.

**Q: How do I stop the bridge?**
A: Call notepadpp_shutdown(confirm=True) or POST /api/shutdown with valid credentials. Restart via start.ps1 or the Tauri operator.

## ADVANCED PATTERNS

### Pattern: Automated Test Loop
1. Open the test file.
2. Run linting on the implementation file.
3. Fix each issue with targeted inserts.
4. Save and re-lint until clean.
5. Save the session so the loop state survives a restart.

### Pattern: Plugin Research
1. Discover plugins by keyword with a small limit.
2. Read the top results and pick one.
3. Install it and list installed plugins to confirm.
4. Execute its main command to verify it works.

### Pattern: Display Recovery
1. Check theme_status to understand the current configuration.
2. Apply fix_invisible_text for rendering issues.
3. If the problem persists, fix_display_issue for a broader refresh.
4. Optionally re-apply the active theme after the fix.

### Pattern: Workspace Handoff
1. List tabs and note the active file.
2. Save the session with a descriptive name.
3. Record the session name in your response to the user.
4. On the next session, load it by name.

## LIMITATIONS TO KNOW

- The server controls one Notepad++ instance on the local machine.
- Buffer-level text is edited through the caret: inserts land at the cursor, not at arbitrary offsets.
- Linting operates on saved files, not unsaved buffers. Save before linting.
- Theme changes apply on the next Notepad++ start.
- Plugin installs are UI-driven and interactive; keep them one at a time.
- The chat LLM is optional; without one, chat returns a routing hint explaining how to enable it.

Use this guide as the reference for phrasing requests so the server maps them to the correct portmanteau operation every time.

## RECOVERY NARRATIVES

### Narrative: "The file was opened but the text is invisible"

What the user sees: the tab exists, the title bar shows the file name, but the editing area appears blank.

What to do:
1. Call display_ops(operation="fix_invisible_text"). The server runs focus and refresh heuristics against the Scintilla window.
2. If that does not help, call display_ops(operation="fix_display_issue") for the broader redraw path.
3. If the problem is theme-related (for example after switching themes), check theme_status and re-apply the intended theme with set_editor_theme.
4. Tell the user what was fixed and ask them to confirm the buffer renders.

### Narrative: "Lint found issues I did not expect"

What the user sees: linting_ops returns issues with severity, line, and column.

What to do:
1. Read the issue list sorted by severity.
2. For each issue, switch to the right tab (tab_ops switch) or open the file (file_ops open).
3. Apply the fix with text_ops insert at the reported location.
4. Save the file (file_ops save) - linting runs on disk, so the file must be saved before re-linting.
5. Re-run linting_ops and confirm the issue count dropped.
6. Report the delta to the user: N issues found, M fixed, remaining K with reasons.

### Narrative: "Session load did not restore my tabs"

What the user sees: session_ops load reports success but the editor shows only one tab.

What to do:
1. Confirm the session file exists with session_ops list and check the file count reported.
2. Verify the user ran load while Notepad++ was closed or after a restart; loading can require relaunching the editor with -openSession.
3. If the session is empty, check whether live session.xml was present at save time; the server falls back to the active tab path when the live session is empty.
4. Re-save the session with a fresh name and retry the load.

### Narrative: "Plugin install appears to hang"

What the user sees: plugin_ops install returned, but no dialog appeared.

What to do:
1. Check that the plugin name came from discover; names must match the official catalog exactly.
2. Check the health of the catalog with a discover call; if it fails, set NOTEPADPP_PLUGIN_LIST_URL to a mirror and retry.
3. Run the install once more and watch for the Plugin Admin UI; installs are UI-automation driven and must not run in parallel.
4. Confirm with plugin_ops list that the DLL is now present.

### Narrative: "Chat returned a routing hint instead of an answer"

What the user sees: the chat page shows the fallback text about the LLM being unreachable.

What to do:
1. Check the Settings page provider status: it probes Ollama, LM Studio, and vLLM.
2. Start the local LLM and confirm a model is listed in the model dropdown.
3. If a provider is running on a non-default port, set AI_ENDPOINT and AI_MODEL in .env accordingly.
4. Retry the chat message.

## PROMPTING GUIDANCE FOR CLAUDE

### Be specific about the target

Weak: "Fix my file."
Strong: "Open C:/Projects/app/parser.py, find the function parse_line, and insert a docstring above it."

The stronger phrasing maps directly to file_ops, text_ops find, and text_ops insert - three deterministic calls instead of guesswork.

### Confirm state before mutating

Always query state first when you are not certain of it:
- Not sure the editor is up? status_ops health_check.
- Not sure which file is active? file_ops info.
- Not sure which tabs exist? tab_ops list.

State queries are cheap and make mutations safe.

### One goal, one plan

For a goal like "clean up this project", produce a numbered plan first:
1. list tabs and identify the files involved
2. lint each implementation file and collect issues
3. fix issues by severity with targeted inserts
4. re-lint to verify
5. save the workspace session for continuity

Then execute the plan step by step, reporting progress after each step. Prefer agentic_notepad_workflow when sampling is available and the goal spans more than three tool calls.

## GLOSSARY

- Active buffer: the document currently displayed in the focused tab.
- Caret: the blinking insertion point; text_ops insert writes here.
- Portmanteau tool: a consolidated tool that takes an operation enum (file_ops, text_ops, tab_ops, session_ops, linting_ops, display_ops, plugin_ops, status_ops).
- Named session: a saved snapshot of all open buffers stored as session XML.
- Live session: Notepad++'s own session.xml that records what was open at exit.
- Plugin catalog: the official nppPluginList JSON with 1,400+ plugins.
- Scintilla window: the low-level editor control Notepad++ is built on; display fixes operate on it.
- Sampling: the MCP mechanism that lets the server call back to an LLM for reasoning; used by suggest_notepad_plan and agentic_notepad_workflow.
- HTTP bridge: the FastAPI server on port 10815 that serves /mcp and /api.
- REST bridge auth: HTTP Basic credentials from MCP_WEB_USER and MCP_WEB_PASSWORD; unset means the API is locked.
- Ring buffer: the in-memory activity log exposed at /api/logs used by the Logging page.
- CUA smoke test: the installer certification flow (install, launch, health, nav walk, uninstall) driven by scripts/cua-smoke.py.
- CORS: browser cross-origin policy; the bridge allows tauri://localhost and LAN/Tailscale origins per the fleet standard.

## FINAL REMINDERS

- Save before linting: linting reads files from disk.
- Snapshot sessions before risky work, not after.
- Ask for clarification when a parameter is missing; the server tells you which parameter and why.
- When an operation fails twice in a row, stop retrying and change approach or ask the user.
- The server is local-first: everything runs on your machine against your Notepad++.

This guide, used together with the system prompt and the example catalog, is everything the model needs to operate Notepad++ reliably and conversationally.
