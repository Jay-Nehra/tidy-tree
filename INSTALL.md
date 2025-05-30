# Installation Guide

## Option 1: Global Tool (Recommended)

Install as a global command that works from any directory:

```bash
uv tool install .
```

If you see a warning about PATH, update your shell configuration:
```bash
uv tool update-shell
```

Then restart your terminal or run:
```bash
# Windows Git Bash/PowerShell
source ~/.bashrc
# or just open a new terminal window
```

Now use `tidy-tree` from anywhere:
```bash
cd ~/Downloads
tidy-tree --apply
```

**Note:** This installs the tool globally, so `tidy-tree` command will be available system-wide without needing to activate any virtual environment.

## Option 2: Development Setup

If you want to modify the code or contribute:

```bash
# Create virtual environment and install dependencies
uv sync

# Activate the virtual environment
source ../.venv/Scripts/activate    # Windows Git Bash
# or use your preferred activation method

# Now tidy-tree command works in this shell
tidy-tree --help
```

## Option 3: Direct Python Execution

You can always run the script directly without installation:

```bash
python src/tidy_tree/standardize_names.py --help
```

## Troubleshooting

**"tidy-tree: command not found" after installation**
- Make sure you used `uv tool install .` (not `uv pip install`)
- Run `uv tool update-shell` to update PATH
- Restart your terminal
- Try running `uv tool list` to see installed tools

**Virtual environment issues**
- If using Option 2, make sure the virtual environment is activated
- You can also use `uv run tidy-tree` without activating

**Permission errors**
- On some systems, you might need to add `--user` flag or use appropriate permissions

## Verification

Test your installation:
```bash
tidy-tree --help
```

You should see the full help output with all available options. 