# Notepad++ MCP Server - Configuration Guide

## Basic Configuration

### Notepad++ Path Settings
The server automatically detects Notepad++ installation. For custom installations:

```json
{
  "notepadpp_path": "C:\\Custom\\Path\\notepad++.exe"
}
```

### Auto-Start Behavior
Control automatic Notepad++ launching:

```json
{
  "auto_start": true
}
```

### Operation Timeouts
Adjust timeouts for slow operations:

```json
{
  "timeout": "60"
}
```

## Environment Variables

### PYTHONPATH
Must include the package directory:

```bash
PYTHONPATH="${PWD}"
```

### Custom Notepad++ Location
```bash
NOTEPADPP_PATH="D:\Program Files\Notepad++\notepad++.exe"
```

### Auto-Start Control
```bash
NOTEPADPP_AUTO_START="true"
```

### Timeout Configuration
```bash
NOTEPADPP_TIMEOUT="45"
```

## Advanced Configuration

### Performance Tuning
For high-performance systems:
- Reduce timeout to 15 seconds
- Enable auto-start
- Use absolute paths

### Resource-Constrained Systems
For slower systems:
- Increase timeout to 120 seconds
- Disable auto-start
- Use relative paths where possible

### Network Environments
For network installations:
- Specify UNC paths for Notepad++
- Configure appropriate timeouts
- Verify network permissions

## Plugin Configuration

### Plugin Installation Paths
Plugins install to Notepad++'s standard plugin directory:
```
%APPDATA%\Notepad++\plugins\
```

### Plugin Dependencies
Some plugins may require additional setup:
- Internet connection for downloads
- Administrator privileges for installation
- Compatible Notepad++ version

## Troubleshooting Configuration

### Diagnostic Settings
Enable detailed logging:
```bash
PYTHONUNBUFFERED="1"
```

### Connection Testing
Verify configuration:
```bash
# Check Notepad++ detection
python -c "from notepadpp_mcp.tools.server import status_ops; status_ops('system_status')"

# Test basic operations
python -c "from notepadpp_mcp.tools.server import file_ops; file_ops('info')"
```

## Configuration Validation

### Required Settings
- Notepad++ installation accessible
- Python environment with required packages
- Proper file system permissions

### Optional Optimizations
- Custom paths for non-standard installations
- Timeout adjustments for network latency
- Auto-start preferences

## Backup and Recovery

### Configuration Backup
Save your settings:
```bash
# Export current configuration
cp manifest.json manifest.json.backup
```

### Recovery Procedures
- Restore from backup configurations
- Reset to default settings
- Reinstall MCPB package

## Platform-Specific Notes

### Windows 10/11
- Full Windows API support
- Standard file permissions
- Administrator privileges when needed

### Windows Server Environments
- May require service account permissions
- Network path considerations
- Timeout adjustments for latency

### Development Environments
- Multiple Notepad++ instances supported
- Debug logging available
- Extensive testing capabilities