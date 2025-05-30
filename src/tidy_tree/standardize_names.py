import os
import re
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import fnmatch


def normalize_name(name):
    """Normalize a name by removing prefix and standardizing format."""
    # Strip existing prefix if present (3 digits followed by space or underscore)
    name_no_prefix = re.sub(r"^\d{3}[ _]", "", name)
    
    # Split into base name and extension to preserve extension case
    path_obj = Path(name_no_prefix)
    base_name = path_obj.stem
    extension = path_obj.suffix
    
    # Normalize base name: replace non-alphanumeric/non-underscore with underscore, lowercase
    base_normalized = re.sub(r"[^a-zA-Z0-9_]+", "_", base_name).lower()
    
    # Combine normalized base with original extension case
    return base_normalized + extension


def is_compliant(name):
    """Check if a name is already compliant with the standard format."""
    # Must start with 3 digits followed by underscore
    prefix_match = re.match(r"^(\d{3})_(.+)$", name)
    if not prefix_match:
        return False
    
    prefix, base_with_ext = prefix_match.groups()
    
    # Check if the base part matches its normalized version
    expected_normalized = normalize_name(base_with_ext)
    return base_with_ext == expected_normalized


def extract_prefix(name):
    """Extract numeric prefix if present, return None if not compliant."""
    if is_compliant(name):
        return name[:3]
    return None


def get_next_available_prefix(used_prefixes):
    """Find the lowest available 3-digit prefix, filling gaps."""
    for i in range(1000):  # 000-999
        prefix = f"{i:03d}"
        if prefix not in used_prefixes:
            return prefix
    raise Exception("No available prefixes (directory has 1000+ items)")


def resolve_name_conflict(base_name, existing_names):
    """Resolve naming conflicts by appending _1, _2, etc."""
    if base_name not in existing_names:
        return base_name
    
    counter = 1
    while True:
        candidate = f"{base_name}_{counter}"
        if candidate not in existing_names:
            return candidate
        counter += 1


def matches_pattern(name, patterns):
    """Check if name matches any of the given patterns."""
    if not patterns:
        return False
    for pattern in patterns:
        if fnmatch.fnmatch(name.lower(), pattern.lower()):
            return True
    return False


def should_process_item(item_type, name, path, include_patterns=None, exclude_patterns=None, 
                       files_only=False, folders_only=False, target_path=None):
    """Determine if an item should be processed based on filters."""
    
    # Check type filters
    if files_only and item_type == "Folder":
        return False
    if folders_only and item_type == "File":
        return False
    
    # Check path filter
    if target_path:
        if not str(path).startswith(str(target_path)):
            return False
    
    # Check exclude patterns
    if exclude_patterns and matches_pattern(name, exclude_patterns):
        return False
    
    # Check include patterns (if specified, only include matching items)
    if include_patterns and not matches_pattern(name, include_patterns):
        return False
    
    return True


def standardize_directory(root, include_hidden=False, ignore_dirs=None):
    """Standardize all files and folders in the directory tree with separate numbering."""
    table = []
    root = Path(root)
    ignore_dirs = set(ignore_dirs or [])
    
    for current_dir, dirs, files in os.walk(root):
        current_path = Path(current_dir)
        rel_path = current_path.relative_to(root)
        
        # Check if current directory should be ignored
        if any(part in ignore_dirs for part in rel_path.parts):
            # Mark any ignored subdirectories
            for d in dirs:
                if d in ignore_dirs:
                    table.append([
                        "Folder", 
                        str(current_path / d), 
                        str(current_path / d), 
                        "Ignored"
                    ])
            continue
        
        # Separate files and folders for independent numbering
        file_entries = []
        folder_entries = []
        
        # Process folders
        for d in dirs:
            if not include_hidden and d.startswith('.'):
                table.append([
                    "Folder", 
                    str(current_path / d), 
                    str(current_path / d), 
                    "Skipped (hidden)"
                ])
                continue
            folder_entries.append(d)
        
        # Process files
        for f in files:
            if not include_hidden and f.startswith('.'):
                table.append([
                    "File", 
                    str(current_path / f), 
                    str(current_path / f), 
                    "Skipped (hidden)"
                ])
                continue
            file_entries.append(f)
        
        # Process folders with their own sequence (000-999)
        if folder_entries:
            folder_results = process_entries(folder_entries, current_path, True)
            table.extend(folder_results)
        
        # Process files with their own sequence (000-999)
        if file_entries:
            file_results = process_entries(file_entries, current_path, False)
            table.extend(file_results)
    
    return table


def process_entries(entries, current_path, is_folder):
    """Process a list of entries (files or folders) with sequential 3-digit numbering."""
    results = []
    entry_type = "Folder" if is_folder else "File"
    
    # Sort entries to ensure consistent ordering
    entries = sorted(entries)
    
    # Track existing compliant entries and their normalized base names
    compliant_entries = []
    non_compliant_entries = []
    
    for entry in entries:
        if is_compliant(entry):
            # Extract the base name without prefix for comparison
            base_without_prefix = entry[4:]  # Remove "000_" prefix
            compliant_entries.append((entry, base_without_prefix))
        else:
            non_compliant_entries.append(entry)
    
    # Sort all entries by their normalized base names for consistent ordering
    all_normalized = []
    
    # Add compliant entries
    for original_name, base_name in compliant_entries:
        all_normalized.append((original_name, base_name, True))  # True = was compliant
    
    # Add non-compliant entries
    for original_name in non_compliant_entries:
        normalized_base = normalize_name(original_name)
        all_normalized.append((original_name, normalized_base, False))  # False = was not compliant
    
    # Sort by normalized base name for consistent ordering
    all_normalized.sort(key=lambda x: x[1])
    
    # Track used names to avoid conflicts
    proposed_names = set()
    
    # Assign sequential prefixes
    for index, (original_name, normalized_base, was_compliant) in enumerate(all_normalized):
        prefix = f"{index:03d}"
        new_name = f"{prefix}_{normalized_base}"
        
        # Resolve conflicts
        final_name = resolve_name_conflict(new_name, proposed_names)
        proposed_names.add(final_name)
        
        # Determine if this is a change
        if original_name == final_name:
            action = "Unchanged"
        else:
            action = "Renamed"
        
        results.append([
            entry_type,
            str(current_path / original_name),
            str(current_path / final_name),
            action
        ])
    
    return results


def save_markdown_table(table, output_path, editable=False):
    """Save the results table as a Markdown file."""
    if editable:
        lines = [
            "# Standardization Plan (Editable)",
            "",
            "**Instructions:**",
            "- Edit the 'New Name' column to customize the new names",
            "- Delete entire rows to skip those changes",
            "- Keep the table format intact",
            "- Run `tidy-tree --execute` to apply changes from this file",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "| Type | Original Name | New Name | Action | Notes |",
            "|------|---------------|----------|--------|-------|"
        ]
        
        for row in table:
            # Extract just the filename from full paths for cleaner display
            original_name = Path(row[1]).name
            new_name = Path(row[2]).name
            notes = "✏️ Editable" if row[3] == "Renamed" else ""
            lines.append(f"| {row[0]} | {original_name} | {new_name} | {row[3]} | {notes} |")
    else:
        lines = [
            "# Standardization Preview",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "| Type | Original Name | New Name | Action |",
            "|------|---------------|----------|--------|"
        ]
        
        for row in table:
            # Extract just the filename from full paths for cleaner display
            original_name = Path(row[1]).name
            new_name = Path(row[2]).name
            lines.append(f"| {row[0]} | {original_name} | {new_name} | {row[3]} |")
    
    Path(output_path).write_text("\n".join(lines), encoding="utf-8")


def read_plan_from_markdown(plan_path):
    """Read the execution plan from an edited markdown file."""
    plan_path = Path(plan_path)
    if not plan_path.exists():
        return []
    
    content = plan_path.read_text(encoding="utf-8")
    lines = content.split('\n')
    
    # Find the table start
    table_started = False
    changes = []
    
    for line in lines:
        line = line.strip()
        if not table_started:
            if line.startswith('| Type |') or line.startswith('|---'):
                table_started = True
            continue
        
        if line.startswith('|') and not line.startswith('|---'):
            # Parse table row
            parts = [part.strip() for part in line.split('|')[1:-1]]  # Remove empty first/last
            if len(parts) >= 4 and parts[0] in ['File', 'Folder']:
                item_type, original_name, new_name, action = parts[:4]
                if action == "Renamed":
                    changes.append({
                        'type': item_type,
                        'original_name': original_name,
                        'new_name': new_name,
                        'action': action
                    })
    
    return changes


def apply_renames(table, include_patterns=None, exclude_patterns=None, files_only=False, 
                 folders_only=False, target_path=None, cwd=None):
    """Apply the rename operations with filtering options."""
    if cwd is None:
        cwd = Path.cwd()
    
    # Separate renames into files and folders with filtering
    file_renames = []
    folder_renames = []
    applied_count = 0
    skipped_count = 0
    
    for row in table:
        if row[3] == "Renamed":
            old_path = Path(row[1])
            new_path = Path(row[2])
            item_type = row[0]
            name = old_path.name
            
            # Apply filters
            if not should_process_item(item_type, name, old_path, include_patterns, 
                                     exclude_patterns, files_only, folders_only, target_path):
                skipped_count += 1
                continue
            
            if item_type == "File":
                file_renames.append((old_path, new_path))
            else:
                folder_renames.append((old_path, new_path))
            applied_count += 1
    
    print(f"Applying {applied_count} renames (skipped {skipped_count} due to filters)...")
    
    # Apply file renames first (safer - no path dependency issues)
    for old_path, new_path in file_renames:
        try:
            old_path.rename(new_path)
            print(f"✅ File: {old_path.name} → {new_path.name}")
        except Exception as e:
            print(f"❌ Error renaming file {old_path} → {new_path}: {e}")
    
    # Apply folder renames (process from deepest to shallowest to avoid path issues)
    folder_renames.sort(key=lambda x: len(x[0].parts), reverse=True)
    for old_path, new_path in folder_renames:
        try:
            old_path.rename(new_path)
            print(f"✅ Folder: {old_path.name} → {new_path.name}")
        except Exception as e:
            print(f"❌ Error renaming folder {old_path} → {new_path}: {e}")
    
    return applied_count


def apply_from_plan(plan_path, cwd):
    """Apply renames from an edited plan file."""
    changes = read_plan_from_markdown(plan_path)
    if not changes:
        print("No changes found in plan file.")
        return 0
    
    applied_count = 0
    print(f"Applying {len(changes)} changes from plan file...")
    
    # Group by type and apply in safe order
    file_changes = [c for c in changes if c['type'] == 'File']
    folder_changes = [c for c in changes if c['type'] == 'Folder']
    
    # Apply file changes first
    for change in file_changes:
        # Find the actual file path (search in current directory tree)
        old_name = change['original_name']
        new_name = change['new_name']
        
        # Find the file
        old_path = None
        for root, dirs, files in os.walk(cwd):
            if old_name in files:
                old_path = Path(root) / old_name
                break
        
        if old_path and old_path.exists():
            new_path = old_path.parent / new_name
            try:
                old_path.rename(new_path)
                print(f"✅ File: {old_name} → {new_name}")
                applied_count += 1
            except Exception as e:
                print(f"❌ Error renaming file {old_name} → {new_name}: {e}")
        else:
            print(f"⚠️  File not found: {old_name}")
    
    # Apply folder changes (deepest first)
    folder_paths = []
    for change in folder_changes:
        old_name = change['original_name']
        new_name = change['new_name']
        
        # Find the folder
        old_path = None
        for root, dirs, files in os.walk(cwd):
            if old_name in dirs:
                old_path = Path(root) / old_name
                folder_paths.append((old_path, old_path.parent / new_name, old_name, new_name))
                break
    
    # Sort by depth (deepest first)
    folder_paths.sort(key=lambda x: len(x[0].parts), reverse=True)
    
    for old_path, new_path, old_name, new_name in folder_paths:
        if old_path.exists():
            try:
                old_path.rename(new_path)
                print(f"✅ Folder: {old_name} → {new_name}")
                applied_count += 1
            except Exception as e:
                print(f"❌ Error renaming folder {old_name} → {new_name}: {e}")
        else:
            print(f"⚠️  Folder not found: {old_name}")
    
    return applied_count


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Standardize file and folder names recursively with 3-digit prefixes.",
        epilog="""
Examples:
  tidy-tree                              # Preview changes
  tidy-tree --apply                      # Apply all changes (quick mode)
  tidy-tree --prepare                    # Generate editable plan
  tidy-tree --execute                    # Apply from edited plan
  tidy-tree --apply --files-only         # Apply only to files
  tidy-tree --apply --exclude "*.zip"    # Exclude ZIP files
  tidy-tree --apply --include "*.pdf"    # Only PDF files
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Main action arguments
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--apply", 
        action="store_true", 
        help="Apply the renames (default is dry-run preview)"
    )
    action_group.add_argument(
        "--prepare", 
        action="store_true", 
        help="Generate an editable plan file (standardization_plan.md)"
    )
    action_group.add_argument(
        "--execute", 
        action="store_true", 
        help="Execute changes from edited plan file"
    )
    
    # Filtering options
    filter_group = parser.add_argument_group('filtering options')
    filter_group.add_argument(
        "--include-hidden", 
        action="store_true", 
        help="Include hidden files and folders (starting with .)"
    )
    filter_group.add_argument(
        "--ignore", 
        action="append", 
        help="Directory name to ignore (can be used multiple times)",
        default=[]
    )
    
    # Selective application options
    selective_group = parser.add_argument_group('selective application (only with --apply)')
    selective_group.add_argument(
        "--files-only", 
        action="store_true", 
        help="Apply changes only to files"
    )
    selective_group.add_argument(
        "--folders-only", 
        action="store_true", 
        help="Apply changes only to folders"
    )
    selective_group.add_argument(
        "--include", 
        action="append", 
        help="Include only items matching pattern (e.g., '*.pdf')",
        default=[]
    )
    selective_group.add_argument(
        "--exclude", 
        action="append", 
        help="Exclude items matching pattern (e.g., '*.zip')",
        default=[]
    )
    selective_group.add_argument(
        "--path", 
        type=Path,
        help="Apply changes only within specific path"
    )
    
    args = parser.parse_args()
    
    # Get current working directory
    cwd = Path.cwd()
    
    # File paths
    preview_path = cwd / "standardization_preview.md"
    plan_path = cwd / "standardization_plan.md"
    
    # Handle different modes
    if args.execute:
        # Execute from plan file
        if not plan_path.exists():
            print(f"❌ Plan file not found: {plan_path}")
            print("Run 'tidy-tree --prepare' first to generate a plan file.")
            return
        
        applied_count = apply_from_plan(plan_path, cwd)
        if applied_count > 0:
            print(f"\n✅ Successfully applied {applied_count} changes from plan file!")
            # Clean up plan file after successful execution
            plan_path.unlink()
            print(f"Cleaned up plan file: {plan_path}")
        else:
            print("\n⚠️  No changes were applied.")
        return
    
    # Generate standardization table
    print("🔍 Analyzing directory structure...")
    result_table = standardize_directory(
        root=cwd,
        include_hidden=args.include_hidden,
        ignore_dirs=args.ignore
    )
    
    if args.prepare:
        # Prepare mode - generate editable plan
        save_markdown_table(result_table, plan_path, editable=True)
        print(f"📝 Editable plan saved to: {plan_path}")
        print("\nNext steps:")
        print("1. Edit the plan file to customize changes")
        print("2. Run 'tidy-tree --execute' to apply your changes")
        
        rename_count = sum(1 for row in result_table if row[3] == "Renamed")
        if rename_count > 0:
            print(f"\nFound {rename_count} items to standardize.")
        else:
            print("\n✅ No changes needed - all items are already standardized!")
        
    elif args.apply:
        # Apply mode with optional filtering
        save_markdown_table(result_table, preview_path)
        print(f"📋 Preview saved to: {preview_path}")
        
        # Apply changes with filtering
        applied_count = apply_renames(
            result_table, 
            include_patterns=args.include if args.include else None,
            exclude_patterns=args.exclude if args.exclude else None,
            files_only=args.files_only,
            folders_only=args.folders_only,
            target_path=args.path,
            cwd=cwd
        )
        
        if applied_count > 0:
            print(f"\n✅ Successfully applied {applied_count} changes!")
        else:
            print("\n⚠️  No changes were applied (all filtered out or already compliant).")
        
    else:
        # Default preview mode
        save_markdown_table(result_table, preview_path)
        print(f"📋 Preview saved to: {preview_path}")
        
        # Print results to console
        print("\nStandardization Results:")
        print("Type\tOriginal Path\tNew Path\tAction")
        for row in result_table:
            print("\t".join(row))
        
        rename_count = sum(1 for row in result_table if row[3] == "Renamed")
        if rename_count > 0:
            print(f"\nDry run complete. Found {rename_count} items to standardize.")
            print("\nNext steps:")
            print("• Quick: 'tidy-tree --apply' to apply all changes")
            print("• Flexible: 'tidy-tree --prepare' to create editable plan")
            print("• Selective: 'tidy-tree --apply --files-only' for targeted changes")
        else:
            print("\n✅ No changes needed - all items are already standardized!")


if __name__ == "__main__":
    main() 