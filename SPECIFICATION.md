# Standardize Names Tool - Corrected Specification

## 1. Overview

A Python-based command-line tool that recursively renames files and folders in the current directory (and its subdirectories) to a consistent format:

- **Lowercase base names** (extensions preserve original case)
- **Spaces & special characters → underscores**
- **3-digit numerical prefixes (000–999)** to enforce ordering
- **Separate numbering for files and folders** in each directory
- **Re-indexing on re-runs** - maintains sequential order
- **Dry-run preview** with Markdown report
- **Optionally apply changes**

## 2. Goals & Use Cases

- One-click cleanup of messy directories (e.g. Downloads, Documents)
- Enforce consistent naming for automation, backups, version control
- Safe "preview" mode to audit before renaming
- Repeatable: maintains clean sequential numbering on multiple runs

## 3. Core Features

| Feature | Behavior |
|---------|----------|
| **Recursive Traversal** | Walk entire tree under the current working directory |
| **Dry-Run (default)** | List all proposed renames in a Markdown table (`standardization_preview.md`) |
| **Apply Mode** | With `--apply`, perform the actual `os.rename()` operations after dry-run review |
| **Normalization** | • Strip existing 3-digit prefix if present (NNN_ or NNN )<br>• Replace any non-alphanumeric/dot/underscore with `_`<br>• Lowercase base name only (preserve extension case) |
| **3-Digit Prefixes** | • Assign sequential 000–999 per directory<br>• Separate sequences for files and folders<br>• Reset counters in each subfolder<br>• Re-index on re-runs for gap-free numbering |
| **Stable Re-Runs** | Re-indexes all items to maintain sequential order, preserving compliant base names |
| **Conflict Handling** | If `000_name` would collide, append `_1`, `_2`, etc., based on first free suffix. |
| **Hidden Files** | Skip names beginning with `.` unless `--include-hidden` is passed |
| **Ignore Dirs** | `--ignore DIR_NAME` (can be repeated) to skip entire subtrees matching that folder name |

## 4. Command Syntax

```bash
standardize-names [--apply] [--include-hidden] [--ignore NAME]…
```

- `--apply` Apply the renames (omit to dry-run only)
- `--include-hidden` Include items starting with `.`
- `--ignore NAME` Skip any folder (and its contents) named NAME

## 5. Output & Reporting

**Console:** tab-separated lines:
```
Type    Original Path           New Path                Action
File    ./foo bar.txt          ./000_foo_bar.txt       Renamed
Folder  ./old_project          ./000_old_project       Renamed
```

**Markdown file:** `standardization_preview.md` under CWD, with:

| Type | Original Name | New Name | Action |
|------|---------------|----------|--------|
| File | foo bar.txt | 000_foo_bar.txt | Renamed |
| Folder | old_project | 000_old_project | Renamed |
| Folder | temp_folder | temp_folder | Ignored |

## 6. Compliance Rules

A name is considered **compliant** if:

1. **Starts with exactly 3 digits followed by underscore**: `NNN_`
2. **The part after the prefix is already normalized**: lowercase base name, underscores for special chars, original extension case preserved

Examples:
- ✅ `000_my_document.PDF` (compliant)
- ✅ `001_photo_2023.jpg` (compliant)  
- ❌ `002 my document.pdf` (space instead of underscore)
- ❌ `003_My Document.pdf` (uppercase in base name)
- ❌ `document.pdf` (no prefix)

## 7. Internal Logic

1. **Walk directory tree** with `os.walk()`, processing each directory independently
2. **Skip ignored subtrees** whose path parts include an `--ignore` name
3. **For each directory:**
   - Separate files and folders into independent lists
   - **Process folders:** Sort by normalized name, assign sequential 000-999 prefixes
   - **Process files:** Sort by normalized name, assign sequential 000-999 prefixes  
   - Both sequences start from 000 in each directory
4. **Re-indexing logic:** Even compliant names get re-indexed to maintain perfect sequential order
5. **Dry-Run:** Output table and save Markdown file
6. **Apply Mode:** Perform renames in safe order (files first, then folders depth-first)

## 8. Edge Cases & Constraints

| Case | Behavior |
|------|----------|
| **Huge directories (1000+ items)** | Throw error (only 3-digit prefixes supported per type) |
| **Existing "NNN Name" vs "NNN_Name"** | Only "NNN_Name" format treated as compliant |
| **Mixed-case extensions** | Preserved exactly: `.PDF`, `.JPG` stay as-is |
| **Multiple underscores** | Collapsed to single: `a___b` → `a_b` |
| **Leading/trailing underscores** | Preserved in base name |
| **Name collisions** | Resolved with `_1`, `_2`, etc. |
| **Apply order** | Files first, then folders (deepest to shallowest) |
| **Re-run behavior** | Re-indexes everything for clean sequential numbering |

## 9. Key Features of Current Implementation

1. **3-digit prefixes** - supports up to 1000 items per type per directory
2. **Separate file/folder numbering** - independent 000-999 sequences
3. **Perfect re-indexing** - maintains sequential order on re-runs
4. **Extension case preservation** - base names lowercased, extensions keep original case
5. **Robust conflict resolution** - reliable name collision handling
6. **Correct apply order** - files first, then folders depth-first to avoid path errors
7. **Hybrid workflows** - quick apply, editable plans, and selective filtering

## 10. Advanced Workflows

### Quick Mode
```bash
tidy-tree --apply
```

### Planning Mode  
```bash
tidy-tree --prepare    # Generate editable plan
# Edit standardization_plan.md
tidy-tree --execute    # Apply customized plan
```

### Selective Mode
```bash
tidy-tree --apply --files-only
tidy-tree --apply --include "*.pdf"
tidy-tree --apply --exclude "*.zip"
```

## 11. Future Enhancements

- Undo (`--undo`) using a generated log file
- Config file (`.standardize-config`) for custom rules
- Glob-style excludes enhancement
- Switchable ordering: by name, modified time, creation time
- 4-digit prefixes for extremely large directories
- Max filename length enforcement 