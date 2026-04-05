# Notepad++ macros (editor feature)

This page is **about Notepad++ itself**, not a guarantee that `notepadpp-mcp` exposes every macro operation. It exists so contributors and users share a **mental model** of what macros are, what people use them for, and what **might** be automated safely later.

Official reference (config file format): [npp-user-manual.org — config files / `<Macros>`](https://npp-user-manual.org/docs/config-files/)

---

## What a macro is in Notepad++

- **Recorded or hand-written sequences** of editor actions, stored by Notepad++ and bound to **Macro** menu entries (and optionally **keyboard shortcuts**).
- **Linear playback only**: one action after another. There are **no variables, branches, or loops** in the built-in macro system. Anything that needs decisions (“if selection empty, do X”) is usually done with **plugins**, **scripts**, or **external tools**—not classic macros.
- Actions are stored as low-level steps (mostly **Scintilla messages**, some **Notepad++ commands**, and **find/replace**-style steps). That makes macros **powerful** but also **brittle** if the document layout changes between recording and playback.

So: macros excel at **repeatable mechanical edits** on text that looks like what you had when you recorded.

---

## What people typically use macros for

These are **common patterns** in forums and day-to-day use—not an exhaustive list.

| Kind of task | Examples |
|--------------|----------|
| **Line hygiene** | Trim trailing spaces; normalize indentation on a line; duplicate or join lines; insert a timestamp or file header block. |
| **Encoding / line endings** | Convert CRLF ↔ LF in a controlled way (often combined with **Edit** menu operations); prep for tools that expect Unix line endings. |
| **Boilerplate** | Insert a comment banner, license stub, or function skeleton where the structure is fixed. |
| **Repeated find/replace** | A sequence of small replacements (macros can include **search/replace** steps—see manual for `type` values). |
| **Navigation + edit** | Jump to start/end of line, select word, wrap with quotes—**if** the cursor starts in a predictable place. |
| **House rules** | Personal “clean up this log dump” or “format this CSV-ish block” flows that you run dozens of times per week. |

What macros are **not** great for: refactoring across a whole project with AST awareness, running compilers, or anything that needs **feedback** from the buffer mid-sequence. For that, users lean on **plugins** (e.g. scripting plugins), **external linters**, or **other editors/IDEs** for that slice of work.

---

## Where macros live on disk

- User macros and macro shortcuts are persisted under the user profile, typically:  
  `%APPDATA%\Notepad++\shortcuts.xml`
- The file also holds other shortcut data; the **`<Macros>`** block holds **`<Macro name="...">`** elements with **`<Action .../>`** children.
- **Risk:** Notepad++ may read this at startup and write it on exit. Editing `shortcuts.xml` **while N++ is running** can cause **lost edits** or **conflicts**. Safer workflow: **close Notepad++**, edit a **backup copy**, validate XML, then replace the file and reopen N++.

---

## Curated macro sets (documentation vs shipping snippets)

**Idea A — Documentation-only “curated set”**  
- Maintain **`docs/macros/examples/`** (or similar) with **small, named `.xml` fragments** or **full example `Macros` sections** plus **README** explaining what each does and how to merge manually.  
- **Pros:** No code risk; users learn the editor; easy to review in PRs.  
- **Cons:** Manual merge into `shortcuts.xml`.

**Idea B — Import helper (future MCP / CLI)**  
- **Backup** `shortcuts.xml` → **parse** XML → **append or replace** named `<Macro>` entries from a curated library → **write** atomically → user restarts N++.  
- **Pros:** Repeatable, testable; fits “macro CRUD” for **definitions on disk**.  
- **Cons:** Must handle XML schema quirks, duplicates, and file locking; needs clear **dry-run** and **rollback** story.

**Idea C — Playback (“run macro by name”)**  
- Harder: requires driving the **Notepad++ UI** or **internal command IDs** reliably (window focus, macro menu). Possible with enough **Win32/pywinauto** work but **fragile** across versions and themes.  
- Often better to expose **text operations** directly via existing MCP tools than to simulate macro playback—unless there is strong demand.

---

## “Macro CRUD” — what would be realistic

| Operation | Feasibility | Notes |
|-----------|-------------|--------|
| **List / read** macros (names, shortcuts) | **High** | Parse `shortcuts.xml` read-only. |
| **Create / update / delete** macro definitions | **Medium** | Same file; must coordinate with N++ lifecycle and backups. |
| **Playback** | **Lower** | UI/command automation; version-sensitive. |
| **Record** | **Not practical remotely** | Recording is an interactive editor feature. |

A **good curated set** in-repo starts with **documentation + XML snippets** (Idea A). If that proves useful, **list + import with backup** (subset of CRUD) is the next increment before full edit/delete.

---

## Relation to `notepadpp-mcp`

- Today, **macro behavior is an editor concern**; this server does not replace the **Macro** menu.
- **Possible future alignment:** tools that **read** macro names from `shortcuts.xml`, **validate** curated fragments, or **merge** curated macros with user consent—similar in spirit to theme/config helpers that already touch `%APPDATA%\Notepad++\`.

See also: [EDITOR_AND_MCP_SCOPE.md](EDITOR_AND_MCP_SCOPE.md).
