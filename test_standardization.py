#!/usr/bin/env python3
"""
Test script for the standardization tool.
Creates various edge cases to test the fixed implementation.
"""

import os
import tempfile
import shutil
from pathlib import Path
import subprocess


def create_test_structure(test_dir):
    """Create a complex directory structure with various edge cases."""
    test_dir = Path(test_dir)
    
    # Create various test files and folders with problematic names
    test_cases = [
        # Already compliant names (should be unchanged)
        "00_already_compliant.txt",
        "01_another_compliant",
        "02_compliant_folder",
        
        # Names with spaces and special characters
        "My Document (Final).pdf",
        "Photo 2023-12-01.jpg",
        "Project #1 - Final Version!!!.docx",
        "Music & Videos",
        
        # Names with existing prefixes but wrong format
        "03 Wrong Format.txt",  # space instead of underscore
        "04-hyphen-format.txt",  # hyphen instead of underscore/space
        "05.dot.format.txt",
        
        # Mixed case extensions (should preserve case)
        "Document.PDF",
        "Image.JPG",
        "Archive.ZIP",
        
        # Edge case names
        "___multiple___underscores___",
        "trailing_underscore_",
        "_leading_underscore",
        "numbers123andletters",
        "ALLCAPS",
        "mixedCASE",
        
        # Hidden files (should be skipped unless --include-hidden)
        ".hidden_file",
        ".hidden_folder",
        
        # Files with no extension
        "README",
        "LICENSE",
        "makefile",
    ]
    
    # Create root level items
    for name in test_cases:
        path = test_dir / name
        if name.endswith(('.txt', '.pdf', '.jpg', '.docx', '.PDF', '.JPG', '.ZIP')):
            path.write_text(f"Content of {name}")
        else:
            path.mkdir(exist_ok=True)
    
    # Create subdirectories with their own test cases
    subdir1 = test_dir / "subdir_level1"
    subdir1.mkdir(exist_ok=True)
    
    subdir_cases = [
        "00_sub_compliant.txt",
        "Another File.txt",
        "99_high_number.txt",  # test gap filling
        "01_gap_test.txt",     # this should get 02 in second run
    ]
    
    for name in subdir_cases:
        (subdir1 / name).write_text(f"Content of {name}")
    
    # Create nested subdirectory
    subdir2 = subdir1 / "nested level 2"
    subdir2.mkdir(exist_ok=True)
    (subdir2 / "deep file.txt").write_text("Deep content")
    (subdir2 / "00_deep_compliant.txt").write_text("Deep compliant content")
    
    # Create directory to be ignored
    ignored_dir = test_dir / "temp_folder"
    ignored_dir.mkdir(exist_ok=True)
    (ignored_dir / "should_be_ignored.txt").write_text("This should be ignored")
    
    print(f"Created test structure in: {test_dir}")
    return test_dir


def run_standardization_test(script_path, test_dir, *args):
    """Run the standardization script and return output."""
    cmd = ["python", str(script_path)] + list(args)
    result = subprocess.run(
        cmd, 
        cwd=test_dir, 
        capture_output=True, 
        text=True
    )
    return result.stdout, result.stderr, result.returncode


def compare_implementations(test_dir):
    """Compare old vs new implementation on the same test data."""
    print("=" * 80)
    print("COMPARING OLD VS NEW IMPLEMENTATION")
    print("=" * 80)
    
    # Test original implementation
    print("\n1. Testing ORIGINAL implementation:")
    print("-" * 40)
    stdout_old, stderr_old, code_old = run_standardization_test(
        "legacy/standardization.py", test_dir
    )
    print("STDOUT (Original):")
    print(stdout_old)
    if stderr_old:
        print("STDERR (Original):")
        print(stderr_old)
    
    # Test fixed implementation  
    print("\n2. Testing FIXED implementation:")
    print("-" * 40)
    stdout_new, stderr_new, code_new = run_standardization_test(
        "src/tidy_tree/standardize_names.py", test_dir
    )
    print("STDOUT (Fixed):")
    print(stdout_new)
    if stderr_new:
        print("STDERR (Fixed):")
        print(stderr_new)
    
    # Check for preview files
    old_preview = test_dir / "standardization_preview.md"
    if old_preview.exists():
        print(f"\n3. Original preview file content:")
        print("-" * 40)
        print(old_preview.read_text())
    
    return stdout_old, stdout_new


def test_idempotency(test_dir):
    """Test that running the script multiple times gives consistent results."""
    print("\n" + "=" * 80)
    print("TESTING IDEMPOTENCY (Multiple Runs)")
    print("=" * 80)
    
    # First run (dry run)
    print("\nFirst run (dry-run):")
    stdout1, stderr1, code1 = run_standardization_test(
        "src/tidy_tree/standardize_names.py", test_dir
    )
    print("Lines with 'Renamed':", len([line for line in stdout1.split('\n') if 'Renamed' in line]))
    
    # Apply changes
    print("\nApplying changes:")
    stdout_apply, stderr_apply, code_apply = run_standardization_test(
        "src/tidy_tree/standardize_names.py", test_dir, "--apply"
    )
    print("Apply result:", "SUCCESS" if code_apply == 0 else "FAILED")
    
    # Second run (should show no changes needed)
    print("\nSecond run (should be idempotent):")
    stdout2, stderr2, code2 = run_standardization_test(
        "src/tidy_tree/standardize_names.py", test_dir
    )
    renamed_lines = [line for line in stdout2.split('\n') if 'Renamed' in line]
    print("Lines with 'Renamed':", len(renamed_lines))
    
    if len(renamed_lines) == 0:
        print("✅ IDEMPOTENCY TEST PASSED - No further changes needed")
    else:
        print("❌ IDEMPOTENCY TEST FAILED - Still finding items to rename:")
        for line in renamed_lines:
            print(f"  {line}")


def test_edge_cases(test_dir):
    """Test specific edge cases."""
    print("\n" + "=" * 80)
    print("TESTING EDGE CASES")
    print("=" * 80)
    
    # Test with --include-hidden
    print("\nTesting --include-hidden flag:")
    stdout_hidden, stderr_hidden, code_hidden = run_standardization_test(
        "src/tidy_tree/standardize_names.py", test_dir, "--include-hidden"
    )
    hidden_lines = [line for line in stdout_hidden.split('\n') if 'hidden' in line.lower()]
    print(f"Found {len(hidden_lines)} hidden file operations")
    
    # Test with --ignore
    print("\nTesting --ignore flag:")
    stdout_ignore, stderr_ignore, code_ignore = run_standardization_test(
        "src/tidy_tree/standardize_names.py", test_dir, "--ignore", "temp_folder"
    )
    ignored_lines = [line for line in stdout_ignore.split('\n') if 'Ignored' in line]
    print(f"Found {len(ignored_lines)} ignored operations")


def main():
    """Main test function."""
    print("STANDARDIZATION TOOL TESTING SUITE")
    print("=" * 80)
    
    # Create temporary test directory
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = create_test_structure(temp_dir)
        
        # Make copies for comparison
        original_test_dir = Path(temp_dir) / "original_test"
        fixed_test_dir = Path(temp_dir) / "fixed_test"
        
        shutil.copytree(test_dir, original_test_dir)
        shutil.copytree(test_dir, fixed_test_dir)
        
        # Compare implementations
        compare_implementations(original_test_dir)
        
        # Test idempotency with fixed version
        test_idempotency(fixed_test_dir)
        
        # Test edge cases
        edge_test_dir = Path(temp_dir) / "edge_test"
        shutil.copytree(test_dir, edge_test_dir)
        test_edge_cases(edge_test_dir)
        
        print("\n" + "=" * 80)
        print("TESTING COMPLETE")
        print("=" * 80)
        print(f"Test data was in: {temp_dir}")
        print("Check the output above to verify the fixes work correctly.")


if __name__ == "__main__":
    main() 