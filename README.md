# Tidy Tree

A command-line tool that automatically organizes your messy directories by adding 3-digit prefixes and standardizing file names.

I built this because I got tired of my Downloads folder looking like chaos. This tool recursively walks through directories and gives everything a clean, numbered prefix (000_, 001_, 002_, etc.) while fixing problematic characters in file names.

## What it does

- Adds 3-digit prefixes (000-999) to files and folders for natural ordering
- Files and folders get separate numbering sequences (both start from 000)
- Converts spaces and special characters to underscores
- Preserves file extension casing (.PDF stays .PDF, not .pdf)
- Works recursively through subdirectories
- Each directory gets its own 000-999 numbering sequence for files AND folders
- Re-indexes on re-runs to maintain sequential order
- Won't break already-compliant names, but will re-index them for proper sequencing

## Installation

You need Python 3.8+ and uv (recommended) or pip.

**Global installation (works anywhere):**
```bash
uv tool install .
uv tool update-shell  # If you see a PATH warning
# Restart your terminal
```

**Development installation:**
```bash
uv sync
source ../.venv/Scripts/activate  # Windows Git Bash
# or activate your virtual environment however you prefer
```

After installation, you can run `tidy-tree` from any directory.

## Basic usage

```bash
# See what changes would be made (safe preview)
tidy-tree

# Actually apply the changes
tidy-tree --apply

# Ignore certain folders
tidy-tree --ignore temp_files --ignore node_modules

# Include hidden files (normally skipped)
tidy-tree --include-hidden
```

## Advanced workflows

**Quick mode (for simple cleanup):**
```bash
tidy-tree --apply
```

**Planning mode (for complex directories):**
```bash
# Generate an editable plan
tidy-tree --prepare

# Edit the generated standardization_plan.md file
# Remove rows you don't want, customize names, etc.

# Apply your customized plan
tidy-tree --execute
```

**Selective application:**
```bash
# Only rename files, leave folders alone
tidy-tree --apply --files-only

# Only process PDF files
tidy-tree --apply --include "*.pdf"

# Skip ZIP archives
tidy-tree --apply --exclude "*.zip"

# Only process a specific subdirectory
tidy-tree --apply --path subfolder/
```

## Examples

**Before:**
```
Downloads/
├── Important Document (Final Version).pdf
├── My Presentation [Draft].pptx
├── Old Project Folder
├── image-2023.jpg
└── New folder/
    ├── another file.txt
    └── some data.csv
```

**After:**
```
Downloads/
├── 000_important_document_final_version_.pdf
├── 001_my_presentation_draft_.pptx
├── 002_image_2023.jpg
├── 000_old_project_folder/
└── 001_new_folder/
    ├── 000_another_file.txt
    └── 001_some_data.csv
```

Notice how:
- Files get their own sequence: 000, 001, 002...
- Folders get their own sequence: 000, 001...
- Each directory restarts numbering for both files and folders
- File extensions keep their original case
- Special characters become underscores

## How the numbering works

Each directory has two independent 000-999 sequences:
- One for files: 000_file1.txt, 001_file2.pdf, 002_file3.doc
- One for folders: 000_folder1/, 001_folder2/, 002_folder3/

On re-runs, the tool maintains sequential order by re-indexing everything:
```
Before: 000_first.txt, 005_third.txt, new_file.txt
After:  000_first.txt, 001_new_file.txt, 002_third.txt
```

This ensures clean, gap-free numbering even when files are added or removed.

## Configuration

The tool automatically skips hidden files (starting with .) unless you use `--include-hidden`.

Use `--ignore` to skip entire directory trees:
```bash
tidy-tree --ignore .git --ignore node_modules --ignore __pycache__
```

## Customizing the plan

When you use `--prepare`, you get an editable markdown file:

```markdown
| Type | Original Name | New Name | Action | Notes |
|------|---------------|----------|--------|-------|
| File | my file.txt | 000_my_file.txt | Renamed | ✏️ Editable |
| File | another.pdf | 001_another.pdf | Renamed | ✏️ Editable |
```

Edit the "New Name" column, delete rows you don't want, then run `tidy-tree --execute`.

## Contributing

This is a personal project, but I'm open to improvements. Feel free to open issues or submit pull requests.

## License

MIT License - use it however you want.
