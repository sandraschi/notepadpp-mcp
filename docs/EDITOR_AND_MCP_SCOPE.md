# Notepad++ (editor) vs this repository (MCP server)

This document is **intentionally split** into two parts:

1. **Notepad++** — what the **editor** is and what it is good at on its own.
2. **This repo (`notepadpp-mcp`)** — what **this MCP server** adds and where its responsibility ends.

Nothing here replaces the official Notepad++ documentation or release notes.

---

## Part 1 — Notepad++ (the editor)

**Notepad++** is a **free, open-source** text and source-code editor for **Windows**. It is built on the **Scintilla** editing component and is distributed under the **GNU General Public License v2.0** (or later, per the project’s licensing). Development is public, with a long-lived community around releases, plugins, and translations.

### Why people use it (editor-side strengths)

- **Native Windows application**  
  Runs as a normal Win32 program: typically **fast startup** and **low overhead** compared to heavyweight, web-technology IDEs. That matters for quick edits, large log files, and machines where a full IDE feels heavy.

- **Scintilla-based editing**  
  The core editor provides **syntax highlighting**, **code folding**, **brace matching**, **bookmarking**, and related editing affordances across many languages. You get a serious editing surface—not a minimal Notepad clone.

- **Multi-document workflow**  
  **Tabbed documents**, **split views**, and **session** concepts support working with many files at once and returning to a prior layout. That fits real-world “many configs, many logs, many snippets” work.

- **Search and replace**  
  **Find in files**, **regular expressions**, and multi-line operations are first-class for many users. For refactoring, data cleanup, or auditing codebases, this is often a reason people stay in Notepad++.

- **Column / block editing**  
  **Column mode** (block selection) and related multi-cursor-style workflows are widely used for aligned edits (CSV-like data, tables, repetitive line prefixes).

- **Macros**  
  **Macro recording and playback** lets users automate repetitive edits **inside** the editor without writing a full plugin. That is distinct from external automation.

- **Plugin ecosystem**  
  **Plugin Admin** (and the wider plugin catalog) extends the editor with comparators, spell-check, additional language support, tooling hooks, and more. Plugins are a major reason Notepad++ remains capable for specialized workflows.

- **Customization**  
  **Shortcuts**, **themes**, **user-defined languages**, and extensive **preferences** let teams and individuals standardize how the editor behaves.

- **Localization**  
  The UI is translated into many languages, which matters for global teams and contributors.

- **Community and governance**  
  There is an active **user and contributor base** (forums, issue trackers, translations, plugins). The project’s **home site and repository** are the canonical sources for downloads, security notices, and feature changes.

### What Part 1 is not

- It is **not** a description of this MCP repository.
- It is **not** a promise that every Notepad++ feature is exposed or controllable through `notepadpp-mcp`.

---

## Part 2 — This repository (`notepadpp-mcp`)

**`notepadpp-mcp`** is a **Model Context Protocol (MCP) server** written in **Python**. It runs on **Windows** and talks to a running Notepad++ instance (and related OS/editor surfaces) so that **MCP-capable clients** (e.g. certain IDEs and assistants) can invoke **tools** instead of you clicking every step by hand.

### What this repo provides

- **MCP tools (portmanteau design)** — consolidated tools with `operation` parameters covering areas such as **files**, **tabs**, **text**, **sessions**, **linting**, **display/theme-related helpers**, **plugin discovery/listing/install flows** (as implemented), **status/help**, and **agentic orchestration** where enabled. Exact names and operations are listed in the main **README** and in code.
- **Transport** — typically **stdio** for MCP hosts; optional **HTTP bridge** where implemented.
- **Optional AI / sampling hooks** — configuration for **OpenAI-compatible** or **client-side** sampling, used by higher-level workflows when you enable them.
- **Optional web UI** — a separate front-end package (e.g. under `web_sota/`) may ship alongside the server; see repo layout and README for ports and usage.

### Boundaries (what this repo is not)

- **Not a fork or patch of Notepad++** — it does not ship the editor and does not change Notepad++ licensing.
- **Not a complete remote control of every Scintilla or UI feature** — only what is implemented via the server’s bridge (pywin32, editor integration, plugin/lint paths, etc.) is available to agents.
- **Not a substitute for learning Notepad++** — power-user features (macros, deep plugin behavior, manual settings) remain **editor knowledge**; the server may only automate a **subset** aligned with its tools.

### How to read the two parts together

| Layer | Role |
|--------|------|
| **Notepad++** | The editor you use; features, plugins, and UX live here. |
| **`notepadpp-mcp`** | An **external automation bridge** for MCP clients; scope is defined by its tools and implementation. |

When something is missing from the server, it may still exist **in the editor**—and vice versa: server features may combine editor access with extra logic (linting on PATH, HTTP API, etc.) that is **not** a built-in Notepad++ menu item.

---

## See also

- Main **README** at the repository root — installation, transports, tool tables, troubleshooting.
- [NOTEPADPP_MACROS.md](NOTEPADPP_MACROS.md) — what Notepad++ macros are for, typical uses, storage in `shortcuts.xml`, curated-set ideas, and realistic “macro CRUD” for a future MCP.
- `src/notepadpp_mcp/docs/` — internal examples and notes where present.
- Official Notepad++ project pages for **downloads**, **changelog**, and **community** links.
