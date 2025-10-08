# Scripts Directory

**Automation scripts for notepadpp-mcp repository**

---

## 📋 **Available Scripts**

### **1. Build MCPB Package**
📄 `build-mcpb-package.ps1`

**Purpose**: Build production MCPB package for Claude Desktop

**Usage**:
```powershell
# Build without signing (development)
.\scripts\build-mcpb-package.ps1 -NoSign

# Build with signing (production - when configured)
.\scripts\build-mcpb-package.ps1

# Build with custom output directory
.\scripts\build-mcpb-package.ps1 -OutputDir "C:\builds"

# Show help
.\scripts\build-mcpb-package.ps1 -Help
```

**Output**: `dist/notepadpp-mcp.mcpb` (0.19 MB)

---

### **2. Repository Backup**
📄 `backup-repo.ps1`

**Purpose**: Create complete repository backup as git bundle

**Usage**:
```powershell
# Create backup with defaults
.\scripts\backup-repo.ps1

# Custom backup location and retention
.\scripts\backup-repo.ps1 -BackupDir "E:\Backups" -KeepDays 60
```

**Output**: `D:\Backups\notepadpp-mcp\notepadpp-mcp_[timestamp].bundle`

**Features**:
- ✅ Complete repository backup (all commits, branches, tags)
- ✅ Automatic integrity verification
- ✅ Auto-cleanup of old backups
- ✅ Can restore anywhere

**Restore**:
```powershell
git clone D:\Backups\notepadpp-mcp\[bundle-file].bundle restored-repo
```

---

## 🔧 **Automation Setup**

### **Automated Daily Backups (Recommended)**

Setup Windows Task Scheduler to run `backup-repo.ps1` daily:

```powershell
# Run as Administrator
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"D:\Dev\repos\notepadpp-mcp\scripts\backup-repo.ps1`""

$Trigger = New-ScheduledTaskTrigger -Daily -At 3:00AM

$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable

Register-ScheduledTask -TaskName "Notepadpp-MCP Backup" `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Daily backup of notepadpp-mcp repository"
```

**Verify**:
```powershell
Get-ScheduledTask -TaskName "Notepadpp-MCP Backup"
```

---

## 📚 **Related Documentation**

For complete repository protection strategy, see:

**[Repository Protection Documentation](../docs/repository-protection/README.md)**

Includes:
- Branch protection setup
- Branch strategy & AI workflow
- Backup & recovery guide
- Emergency procedures

---

## 🎯 **Quick Reference**

| Task | Script | Command |
|------|--------|---------|
| Build MCPB | `build-mcpb-package.ps1` | `.\scripts\build-mcpb-package.ps1 -NoSign` |
| Backup repo | `backup-repo.ps1` | `.\scripts\backup-repo.ps1` |
| Show help | Any script | `.\scripts\[script].ps1 -Help` |

---

*Scripts Documentation*  
*Updated: October 8, 2025*  
*Location: `scripts/`*

