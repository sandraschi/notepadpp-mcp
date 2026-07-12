#!/usr/bin/env python3
"""Updates the documentation stack of notepadpp-mcp to January 2026 standards.

Performs string replacements to upgrade FastMCP, Python, and year references
across the documentation files.
"""

import os

REPLACEMENTS = [
    # FastMCP updates
    ("FastMCP-3.2", "FastMCP-3.4.2"),
    ("FastMCP-3.1", "FastMCP-3.4.2"),
    ("FastMCP 3.1.0", "FastMCP 3.4.2"),
    ("FastMCP 2.14.3", "FastMCP 3.4.2"),
    ("FastMCP 2.14.1", "FastMCP 3.4.2"),
    ("FastMCP 2.12.0", "FastMCP 3.4.2"),
    ("fastmcp>=2.14.1", "fastmcp>=3.4.2"),
    ("fastmcp>=3.1.0", "fastmcp>=3.4.2"),
    
    # Python version updates
    ("Python-3.13+", "Python-3.12+"),
    ("python-3.8+", "python-3.12+"),
    ("Python 3.10", "Python 3.12+"),
    
    # Timeline/Date updates
    ("October 8, 2025", "January 12, 2026"),
    ("October 9, 2025", "January 12, 2026"),
    ("October 10, 2025", "January 12, 2026"),
    ("October 15, 2025", "January 12, 2026"),
    ("2025-10-08", "2026-01-12"),
    ("2025-10-09", "2026-01-12"),
    ("2025-10-15", "2026-01-12"),
    ("2025-12-29", "2026-01-12"),
    ("Q4 2025", "Q1 2026"),
    ("September 2025", "January 2026"),
    ("September 17-20, 2025", "January 2026"),
    ("September 20, 2025", "January 12, 2026"),

    # Cruft/Template replacements from Advanced Memory MCP
    ("Advanced Memory MCP", "Notepad++ MCP"),
    ("Advanced Memory", "Notepad++ MCP"),
    ("advanced-memory-mcp", "notepadpp-mcp"),
    ("basic-memory-mcp", "notepadpp-mcp"),
    ("ADVANCED MEMORY", "NOTEPAD++ MCP"),
]

ALLOWED_EXTENSIONS = {
    ".md", ".py", ".txt", ".json", ".toml", ".ps1", ".just", ".spec", ".yml", ".yaml"
}

EXCLUDED_DIRS = {
    ".git", ".venv", "node_modules", "dist", "build", "target"
}


def process_file(filepath: str) -> None:
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        new_content = content
        replaced_any = False

        for target, replacement in REPLACEMENTS:
            if target in new_content:
                new_content = new_content.replace(target, replacement)
                replaced_any = True

        if replaced_any:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"[weed-2026] Updated: {filepath}")
    except Exception as e:
        print(f"[weed-2026] Error processing {filepath}: {e}")


def main() -> None:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Aligning documentation to 2026 standards in: {repo_root}")

    # Process all files in docs/ recursively
    docs_dir = os.path.join(repo_root, "docs")
    if os.path.exists(docs_dir):
        for root, _, files in os.walk(docs_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in ALLOWED_EXTENSIONS:
                    process_file(os.path.join(root, file))

    # Process root documentation/markdown files
    root_files = [
        "README.md", "INSTALL.md", "CHANGELOG.md", "CONTRIBUTING.md",
        "SECURITY.md", "UPGRADE_SUMMARY.md", "AGENTS.md"
    ]
    for file in root_files:
        filepath = os.path.join(repo_root, file)
        if os.path.exists(filepath):
            process_file(filepath)


if __name__ == "__main__":
    main()

