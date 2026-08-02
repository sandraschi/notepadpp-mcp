"""Fleet README.md Orchestration Demo for Notepad++ MCP.

Scans the D:\\Dev\\repos workspace for the top 10 most important fleet
repositories and opens their README.md files in Notepad++ tabs safely.
"""

import asyncio
import subprocess
import sys
from pathlib import Path

# Add src to python path to resolve imports if run from root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

try:
    from notepadpp_mcp.tools.controller import NotepadPPController

    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False


async def main():
    print("Notepad++ Fleet Readme Orchestration Demo")
    print("=============================================")

    if not WINDOWS_AVAILABLE:
        print("Error: This demo requires Windows and the pywin32 library.")
        sys.exit(1)

    # 1. Initialize and verify Notepad++ controller
    controller = NotepadPPController()
    try:
        await controller.ensure_notepadpp_running()
        print(f"Connected to Notepad++ (HWND: {controller.hwnd})")
    except Exception as e:
        print(f"Error: Could not connect to/start Notepad++: {e}")
        sys.exit(1)

    # 2. Scan workspace repositories under D:\\Dev\\repos
    workspace_root = Path(r"D:\Dev\repos")
    print(f"Scanning workspace: {workspace_root}")

    # Top 10 important repositories in the fleet
    important_repos = [
        "notepadpp-mcp",
        "osc-mcp",
        "autohotkey-mcp",
        "sysinternals-mcp",
        "advanced-memory-mcp",
        "browser-mcp",
        "docker-mcp",
        "filesystem-mcp",
        "git-github-mcp",
        "obs-mcp",
    ]

    found_readmes = []

    # First extract from important list
    for repo_name in important_repos:
        repo_path = workspace_root / repo_name
        readme_path = repo_path / "README.md"
        if readme_path.is_file():
            found_readmes.append(readme_path)

    # If we need more, scan other subfolders
    if len(found_readmes) < 10:
        try:
            for p in workspace_root.iterdir():
                if p.is_dir() and p.name not in important_repos and not p.name.startswith("."):
                    readme_path = p / "README.md"
                    if readme_path.is_file():
                        found_readmes.append(readme_path)
                        if len(found_readmes) >= 10:
                            break
        except OSError as e:
            print(f"Warning: Workspace scan encountered an error: {e}")

    # Cap to exactly 10
    found_readmes = found_readmes[:10]

    if not found_readmes:
        print("No README.md files found in the fleet workspace.")
        sys.exit(0)

    print(f"Found {len(found_readmes)} README files to open.")

    # 3. Open each README safely in a new tab
    for i, readme in enumerate(found_readmes, 1):
        rel_path = readme.relative_to(workspace_root)
        print(f"[{i}/{len(found_readmes)}] Opening {rel_path} ...")

        # Launching via command line ensures a new tab is opened safely without overwriting buffers
        subprocess.Popen([controller.notepadpp_exe, str(readme)])
        await asyncio.sleep(0.3)

    print("\nSuccess! Opened fleet READMEs in Notepad++ tabs.")


if __name__ == "__main__":
    asyncio.run(main())
