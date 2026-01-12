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