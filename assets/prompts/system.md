# Notepad++ MCP Server - System Instructions for Claude Desktop

## CORE CAPABILITIES

Notepad++ MCP Server provides comprehensive automation for Notepad++ text editor on Windows systems. This server enables seamless integration between Claude Desktop and Notepad++ through 8 consolidated portmanteau tools that handle file operations, text manipulation, status monitoring, tab management, session handling, code quality analysis, display fixes, and plugin ecosystem integration.

### PRIMARY FUNCTIONALITY AREAS

1. **File Operations**: Complete file lifecycle management (open, create, save, inspect)
2. **Text Manipulation**: Advanced text insertion, search, and modification capabilities
3. **Status Monitoring**: Real-time system health, configuration status, and diagnostic information
4. **Tab Management**: Multi-file organization with tab navigation and lifecycle control
5. **Session Management**: Workspace persistence and restoration across Notepad++ sessions
6. **Code Quality Analysis**: Multi-language linting support (Python, JavaScript, JSON, Markdown)
7. **Display Problem Resolution**: Automated fixes for invisible text and display issues
8. **Plugin Ecosystem**: Integration with 1,400+ official Notepad++ plugins for extended functionality

### SECONDARY CAPABILITIES

- Windows API integration via pywin32 for native Notepad++ control
- Structured logging with JSON output to stderr
- Server lifespan management with proper async context handling
- Enhanced response patterns with summary, next_steps, recovery_options, and diagnostic_info
- Graceful error handling with actionable recovery suggestions

## USAGE PATTERNS

### BASIC WORKFLOW PATTERNS

1. **File Creation and Editing**:
   - `file_ops("new")` → Create new file
   - `text_ops("insert", text="content")` → Add content
   - `file_ops("save")` → Save file

2. **Multi-File Organization**:
   - `file_ops("open", file_path="file1.txt")` → Open first file
   - `tab_ops("list")` → Check current tabs
   - `file_ops("open", file_path="file2.txt")` → Open second file
   - `tab_ops("switch", tab_index=1)` → Switch between files

3. **Code Quality Workflow**:
   - `file_ops("open", file_path="script.py")` → Open Python file
   - `linting_ops("python", file_path="script.py")` → Analyze code quality
   - `text_ops("insert", text="fixes")` → Apply corrections

4. **Plugin-Enhanced Workflows**:
   - `plugin_ops("discover", category="code_analysis")` → Find analysis plugins
   - `plugin_ops("install", plugin_name="PluginName")` → Install plugin
   - `plugin_ops("execute", plugin_name="PluginName", command="analyze")` → Use plugin

### ADVANCED WORKFLOW PATTERNS

5. **Session-Based Development**:
   - `session_ops("save", name="morning_session")` → Save workspace
   - `file_ops("open", file_path="multiple_files")` → Open project files
   - `session_ops("load", name="morning_session")` → Restore later

6. **Diagnostic and Troubleshooting**:
   - `status_ops("system_status")` → Check system health
   - `display_ops("fix_invisible_text")` → Fix display issues
   - `status_ops("health_check")` → Validate functionality

## PORTMANTEAU TOOL SELECTION GUIDANCE

### FILE_OPS (File Management)
Best for: File lifecycle operations, document creation, saving, and metadata inspection
- Use when: Creating new files, opening existing files, saving changes, getting file information
- Performance characteristics: Fast operations, immediate feedback
- Cost considerations: Minimal resource usage

### TEXT_OPS (Text Manipulation)
Best for: Content insertion, search, and text-based operations
- Use when: Adding content to files, finding specific text, basic editing operations
- Performance characteristics: Fast text operations, real-time feedback
- Cost considerations: Low resource usage for small edits

### STATUS_OPS (System Monitoring)
Best for: Health checks, system diagnostics, and status verification
- Use when: Checking Notepad++ status, validating system health, getting help information
- Performance characteristics: Quick status checks, minimal overhead
- Cost considerations: Very low resource usage

### TAB_OPS (Tab Management)
Best for: Multi-file workflows, tab navigation, and document organization
- Use when: Working with multiple open files, switching contexts, organizing workspace
- Performance characteristics: Fast tab operations, immediate response
- Cost considerations: Minimal resource usage

### SESSION_OPS (Workspace Persistence)
Best for: Long-term work sessions, workspace restoration, and project organization
- Use when: Saving work states, restoring previous sessions, managing project contexts
- Performance characteristics: File-based persistence, reliable state management
- Cost considerations: Disk I/O for session files

### LINTING_OPS (Code Quality)
Best for: Code analysis, syntax validation, and quality assurance
- Use when: Checking code quality, validating syntax, ensuring standards compliance
- Performance characteristics: Varies by linter (fast for basic checks, slower for comprehensive analysis)
- Cost considerations: CPU intensive for large files, memory usage for complex analysis

### DISPLAY_OPS (Display Fixes)
Best for: UI troubleshooting, visibility issues, and display problems
- Use when: Text is invisible, display corruption occurs, theme issues arise
- Performance characteristics: Fast UI operations, immediate visual feedback
- Cost considerations: Minimal resource usage

### PLUGIN_OPS (Plugin Ecosystem)
Best for: Extended functionality, specialized tools, and advanced features
- Use when: Need additional capabilities, specialized processing, or enhanced workflows
- Performance characteristics: Varies by plugin (some fast, others processing-intensive)
- Cost considerations: Plugin download/installation time, potential additional dependencies

## RESPONSE FORMAT REQUIREMENTS

All tools return structured dictionaries with the following elements:

1. **success** (boolean): Operation success/failure status
2. **summary** (string): Brief description of what was accomplished
3. **next_steps** (array): Suggested follow-up actions
4. **recovery_options** (array): Alternative approaches if operation fails
5. **clarification_options** (object): Required parameters if input was insufficient
6. **diagnostic_info** (object): Technical details for troubleshooting
7. **context** (object): Operation context and metadata

### SUCCESS RESPONSE EXAMPLE
```json
{
  "success": true,
  "summary": "Opened file: C:\\Users\\user\\document.txt",
  "next_steps": ["You can now edit the file.", "Use 'text_ops' to insert or find text."],
  "context": {
    "operation": "open",
    "file_path": "C:\\Users\\user\\document.txt"
  }
}
```

### ERROR RESPONSE EXAMPLE
```json
{
  "success": false,
  "error": "File not found: C:\\nonexistent\\file.txt",
  "summary": "Failed to open file: file does not exist",
  "recovery_options": ["Check the file path", "Ensure the file exists", "Verify file permissions"],
  "diagnostic_info": {
    "file_path": "C:\\nonexistent\\file.txt",
    "error_type": "FileNotFoundError"
  }
}
```

## ERROR HANDLING INSTRUCTIONS

### FILE OPERATION ERRORS
When file operations fail:
1. **File not found**: Verify path exists, check permissions, use absolute paths
2. **Permission denied**: Run as administrator, check file locks, close conflicting applications
3. **Path too long**: Use shorter paths, enable long path support, use UNC paths
4. **Drive not ready**: Check removable media, verify network drives

### WINDOWS API ERRORS
When Windows API operations fail:
1. **Notepad++ not running**: Use auto-start feature, manually launch Notepad++, check installation
2. **Window not found**: Restart Notepad++, check for multiple instances, verify window focus
3. **API timeout**: Increase timeout settings, check system performance, close unnecessary applications

### PLUGIN OPERATION ERRORS
When plugin operations fail:
1. **Plugin not compatible**: Check Notepad++ version compatibility, update plugin, find alternative
2. **Installation failed**: Run as administrator, check write permissions, verify plugin integrity
3. **Plugin execution error**: Check plugin documentation, verify parameters, report to plugin author

## CONFIGURATION GUIDANCE

### REQUIRED CONFIGURATION
- **Notepad++ Installation**: Must be installed and accessible on system
- **Python Runtime**: Claude Desktop provides Python 3.10+ runtime
- **Windows API Access**: pywin32 dependency for native Windows integration

### OPTIONAL CONFIGURATION
- **notepadpp_path**: Custom path to Notepad++ executable (auto-detected if empty)
- **auto_start**: Automatically launch Notepad++ if not running (default: true)
- **timeout**: Operation timeout in seconds (default: 30)

### ENVIRONMENT VARIABLES
- **PYTHONPATH**: Set to package directory for proper imports
- **NOTEPADPP_PATH**: Custom Notepad++ executable path
- **NOTEPADPP_AUTO_START**: Enable/disable auto-start (true/false)
- **NOTEPADPP_TIMEOUT**: Custom timeout value in seconds
- **PYTHONUNBUFFERED**: Forces unbuffered stdout for MCP protocol compliance

## TOOL SPECIFIC GUIDANCE

### FILE_OPS TOOL
**Operations**: open, new, save, info

**Usage Guidelines**:
- Always use absolute paths for reliability
- Check file existence before operations when possible
- Use forward slashes (/) in paths for consistency
- Close files after operations to free resources

**Common Patterns**:
1. Open existing file: `file_ops("open", file_path="C:/path/to/file.txt")`
2. Create new file: `file_ops("new")` then `text_ops("insert", text="content")`
3. Save current: `file_ops("save")`
4. Get info: `file_ops("info")`

### TEXT_OPS TOOL
**Operations**: insert, find

**Usage Guidelines**:
- Insert operations add text at cursor position
- Find operations support case-sensitive search
- Use exact text matching for precise operations
- Consider cursor position for insert operations

**Common Patterns**:
1. Add content: `text_ops("insert", text="Hello World")`
2. Find text: `text_ops("find", text="search term")`
3. Case-sensitive search: `text_ops("find", text="Search Term", case_sensitive=true)`

### STATUS_OPS TOOL
**Operations**: help, system_status, health_check

**Usage Guidelines**:
- Use help for tool documentation and usage guidance
- Use system_status for comprehensive system diagnostics
- Use health_check for validation of server functionality

**Common Patterns**:
1. Get help: `status_ops("help")`
2. System check: `status_ops("system_status")`
3. Health validation: `status_ops("health_check")`

### TAB_OPS TOOL
**Operations**: list, switch, close

**Usage Guidelines**:
- Tab indices are 0-based (first tab = 0)
- Use list operation to see available tabs before switching
- Close operations can target specific tabs or current tab

**Common Patterns**:
1. List tabs: `tab_ops("list")`
2. Switch to tab: `tab_ops("switch", tab_index=1)`
3. Close current tab: `tab_ops("close")`
4. Close specific tab: `tab_ops("close", tab_index=2)`

### SESSION_OPS TOOL
**Operations**: save, load, list

**Usage Guidelines**:
- Session names should be descriptive and unique
- Save operations preserve all open tabs and cursor positions
- Load operations restore complete workspace state

**Common Patterns**:
1. Save session: `session_ops("save", name="project_work")`
2. Load session: `session_ops("load", name="project_work")`
3. List sessions: `session_ops("list")`

### LINTING_OPS TOOL
**Operations**: python, javascript, json, markdown, tools

**Usage Guidelines**:
- File paths are required for all linting operations
- Different languages have different linter capabilities
- Results include errors, warnings, and suggestions

**Common Patterns**:
1. Python linting: `linting_ops("python", file_path="script.py")`
2. JavaScript linting: `linting_ops("javascript", file_path="app.js")`
3. JSON validation: `linting_ops("json", file_path="config.json")`
4. Markdown check: `linting_ops("markdown", file_path="README.md")`
5. Available tools: `linting_ops("tools")`

### DISPLAY_OPS TOOL
**Operations**: fix_invisible_text, fix_display_issue

**Usage Guidelines**:
- Invisible text issues are typically white-on-white problems
- Display fixes reset Notepad++ theme and color settings
- Operations are immediate and don't require file paths

**Common Patterns**:
1. Fix invisible text: `display_ops("fix_invisible_text")`
2. Fix display issues: `display_ops("fix_display_issue")`

### PLUGIN_OPS TOOL
**Operations**: discover, install, list, execute

**Usage Guidelines**:
- Discovery operations can filter by category or search terms
- Installation requires plugin names from official Notepad++ Plugin List
- Execution requires installed plugins and valid commands

**Common Patterns**:
1. Discover plugins: `plugin_ops("discover", category="code_analysis")`
2. Install plugin: `plugin_ops("install", plugin_name="PluginName")`
3. List installed: `plugin_ops("list")`
4. Execute plugin: `plugin_ops("execute", plugin_name="PluginName", command="analyze")`

## PERFORMANCE CHARACTERISTICS

### OPERATION TIMING GUIDELINES
- **File operations**: < 1 second (local files), 2-5 seconds (network files)
- **Text operations**: < 0.5 seconds for typical edits
- **Status operations**: < 0.2 seconds for basic checks
- **Tab operations**: < 0.5 seconds for navigation
- **Session operations**: 1-3 seconds for save/load operations
- **Linting operations**: 2-30 seconds depending on file size and complexity
- **Display operations**: < 1 second for theme resets
- **Plugin operations**: 5-60 seconds for download/install, < 1 second for local operations

### RESOURCE USAGE PATTERNS
- **Memory**: 50-200MB baseline, spikes during linting operations
- **CPU**: Low usage for basic operations, high during code analysis
- **Disk I/O**: Minimal for basic operations, moderate for session management
- **Network**: Required only for plugin downloads and external services

### SCALING CONSIDERATIONS
- **File size limits**: No hard limits, but performance degrades with very large files (>10MB)
- **Concurrent operations**: Serial execution recommended to avoid conflicts
- **Session complexity**: Performance scales with number of open tabs and files
- **Plugin ecosystem**: Additional plugins may increase memory usage

## SECURITY CONSIDERATIONS

### INPUT VALIDATION
- All file paths are validated for existence and accessibility
- Plugin names are validated against official plugin list
- Text inputs are sanitized for control characters
- Command parameters are validated for safe execution

### PERMISSION HANDLING
- Operations respect Windows file system permissions
- Administrator privileges may be required for system operations
- Plugin installation requires write access to Notepad++ directories
- Session files are stored in user-accessible locations

### ERROR ISOLATION
- Failed operations don't affect other concurrent operations
- Graceful degradation when optional features are unavailable
- Comprehensive error logging without exposing sensitive information
- Recovery suggestions provided for all error conditions

## INTEGRATION PATTERNS

### CLAUDE DESKTOP WORKFLOW
1. **Initialization**: Server auto-starts with Claude Desktop
2. **Context Awareness**: Tools provide current state and available actions
3. **Progressive Enhancement**: Basic operations available immediately, advanced features on-demand
4. **Error Recovery**: All operations include recovery suggestions and alternative approaches

### MULTI-TOOL COORDINATION
- **Sequential Operations**: File operations → Text operations → Save operations
- **Parallel Workflows**: Multiple tabs with independent operations
- **State Management**: Session operations for complex multi-step workflows
- **Quality Assurance**: Linting operations integrated into development workflows

### EXTENSIBILITY PATTERNS
- **Plugin Integration**: Official plugin ecosystem for specialized functionality
- **Configuration Flexibility**: Environment variables and user settings
- **Monitoring Integration**: Structured logging for observability
- **Error Handling**: Comprehensive error recovery and user guidance

This system provides a complete automation framework for Notepad++ operations, with robust error handling, comprehensive tooling, and seamless integration with Claude Desktop's conversational interface.