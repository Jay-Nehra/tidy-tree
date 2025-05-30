"""
Tidy Tree - A command-line tool to standardize file and directory names recursively with 2-digit prefixes.
"""

__version__ = "0.1.0"
__author__ = "jayant-nehra"

# Import main functions for easy access
from .standardize_names import (
    standardize_directory,
    normalize_name,
    is_compliant,
    save_markdown_table,
    apply_renames
) 