# Notepad++ MCP Server - Troubleshooting Guide

## Connection Issues

### "Notepad++ not found"
**Symptoms**: Operations fail with "Notepad++ process not detected"

**Solutions**:
1. Verify Notepad++ is installed
2. Check installation path in configuration
3. Set custom path if needed:
   ```json
   {
     "notepadpp_path": "C:\\Program Files\\Notepad++\\notepad++.exe"
   }
   ```
4. Enable auto-start feature

### "Windows API not available"
**Symptoms**: pywin32 errors, Windows integration failures

**Solutions**:
1. Install pywin32: `pip install pywin32`
2. Restart Claude Desktop
3. Verify Windows API access
4. Check administrator privileges

## File Operation Problems

### "File not found"
**Symptoms**: File operations fail with path errors

**Solutions**:
1. Use absolute paths: `C:\Users\username\Documents\file.txt`
2. Verify file exists in File Explorer
3. Check file permissions
4. Ensure correct path separators (backslashes on Windows)

### "Permission denied"
**Symptoms**: Access denied when opening/saving files

**Solutions**:
1. Run Claude Desktop as administrator
2. Check file ownership and permissions
3. Close conflicting applications
4. Verify antivirus exclusions

### "File locked by another process"
**Symptoms**: Cannot save or modify files

**Solutions**:
1. Close the file in other applications
2. Check for running processes
3. Use Task Manager to identify conflicts
4. Restart applications if needed

## Text Operation Issues

### "Text not inserted"
**Symptoms**: Text insertion operations fail silently

**Solutions**:
1. Verify file is open and editable
2. Check cursor position
3. Ensure file is not read-only
4. Try with smaller text blocks

### "Search not working"
**Symptoms**: Text search finds nothing or incorrect results

**Solutions**:
1. Check case sensitivity settings
2. Verify exact text matching
3. Use smaller search terms
4. Check file encoding

## Tab Management Problems

### "Cannot switch tabs"
**Symptoms**: Tab switching operations fail

**Solutions**:
1. Verify tab exists: `tab_ops("list")`
2. Use 0-based indexing (first tab = 0)
3. Ensure Notepad++ window is active
4. Check for modal dialogs

### "Tab operations slow"
**Symptoms**: Tab operations take unusually long

**Solutions**:
1. Close unnecessary tabs
2. Reduce number of open files
3. Check system memory usage
4. Restart Notepad++ if needed

## Session Management Issues

### "Session not saved"
**Symptoms**: Session save operations fail

**Solutions**:
1. Check write permissions for session directory
2. Ensure unique session names
3. Verify sufficient disk space
4. Close unnecessary applications

### "Session not loading"
**Symptoms**: Cannot restore saved sessions

**Solutions**:
1. Verify session file exists
2. Check session file permissions
3. Ensure original files still exist
4. Try loading different sessions

## Code Quality Problems

### "Linting not working"
**Symptoms**: Code analysis operations fail or return no results

**Solutions**:
1. Verify file extension matches language
2. Check file syntax is valid
3. Ensure linter tools are available
4. Try with smaller files first

### "Slow linting performance"
**Symptoms**: Code quality checks take too long

**Solutions**:
1. Use smaller files for analysis
2. Close unnecessary applications
3. Check system resources
4. Consider file size limits

## Display and Visual Issues

### "Text invisible"
**Symptoms**: White text on white background

**Solutions**:
1. Use: `display_ops("fix_invisible_text")`
2. Restart Notepad++
3. Reset to default theme
4. Check theme settings

### "Display corruption"
**Symptoms**: Garbled or incorrect visual display

**Solutions**:
1. Use: `display_ops("fix_display_issue")`
2. Restart Notepad++
3. Update graphics drivers
4. Reset Notepad++ settings

## Plugin Operation Errors

### "Plugin installation failed"
**Symptoms**: Plugin downloads or installations fail

**Solutions**:
1. Check internet connection
2. Run as administrator
3. Verify plugin compatibility
4. Check available disk space

### "Plugin not working"
**Symptoms**: Installed plugins don't function

**Solutions**:
1. Restart Notepad++
2. Verify plugin is enabled
3. Check plugin documentation
4. Update plugin to latest version

## Performance Issues

### "Operations too slow"
**Symptoms**: General slowness across all operations

**Solutions**:
1. Check system resources (CPU, memory)
2. Close unnecessary applications
3. Restart Notepad++ and Claude Desktop
4. Reduce concurrent operations

### "Memory usage high"
**Symptoms**: High memory consumption

**Solutions**:
1. Close unnecessary tabs
2. Restart applications periodically
3. Monitor system resources
4. Consider file size limits

## System-Level Problems

### "Server not responding"
**Symptoms**: All operations fail, no response

**Solutions**:
1. Restart Claude Desktop
2. Check Claude Desktop logs
3. Verify MCP server configuration
4. Reinstall MCPB package

### "Configuration lost"
**Symptoms**: Custom settings reset

**Solutions**:
1. Check configuration file permissions
2. Restore from backups
3. Reconfigure settings
4. Verify Claude Desktop settings

## Diagnostic Procedures

### Health Check Process
1. Run: `status_ops("health_check")`
2. Check: `status_ops("system_status")`
3. Verify: Notepad++ is running
4. Test: Basic file operations

### Log Analysis
1. Enable debug logging
2. Check Claude Desktop developer console
3. Review operation error messages
4. Identify patterns in failures

### System Validation
1. Verify Notepad++ installation
2. Check Windows API access
3. Validate file system permissions
4. Test network connectivity (for plugins)

## Recovery Procedures

### Complete Reset
1. Uninstall MCPB package
2. Restart Claude Desktop
3. Clear Claude Desktop cache
4. Reinstall MCPB package

### Configuration Reset
1. Remove custom configurations
2. Use default settings
3. Reconfigure step-by-step
4. Test after each change

### Emergency Recovery
1. Use command-line tools directly
2. Access files through File Explorer
3. Manually edit configuration files
4. Contact support if needed

## Getting Additional Help

### Built-in Help
- Use: `status_ops("help")` for tool documentation
- Check: `status_ops("system_status")` for diagnostics
- Review: Error messages for specific guidance

### External Resources
- Notepad++ official documentation
- Claude Desktop troubleshooting guides
- GitHub issues and discussions
- Community forums and support

### Support Information
For additional assistance:
1. Gather diagnostic information
2. Document exact error messages
3. Include system configuration details
4. Provide steps to reproduce issues