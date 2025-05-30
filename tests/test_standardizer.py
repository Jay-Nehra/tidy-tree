"""
Tests for the FileStandardizer class.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock

from src.tidy_tree.standardizer import FileStandardizer, NameChange


class TestFileStandardizer:
    """Test cases for FileStandardizer."""
    
    def test_init_default_values(self):
        """Test initialization with default values."""
        standardizer = FileStandardizer()
        assert standardizer.case_style == "snake"
        assert standardizer.exclude_patterns == []
        assert standardizer.verbose is False
    
    def test_init_custom_values(self):
        """Test initialization with custom values."""
        exclude_patterns = ["*.tmp", "temp*"]
        standardizer = FileStandardizer(
            case_style="kebab",
            exclude_patterns=exclude_patterns,
            verbose=True
        )
        assert standardizer.case_style == "kebab"
        assert standardizer.exclude_patterns == exclude_patterns
        assert standardizer.verbose is True
    
    def test_should_exclude_default_patterns(self):
        """Test exclusion of default patterns."""
        standardizer = FileStandardizer()
        
        # Test default exclusions
        assert standardizer._should_exclude(Path(".git"))
        assert standardizer._should_exclude(Path(".gitignore"))
        assert standardizer._should_exclude(Path("__pycache__"))
        assert standardizer._should_exclude(Path("node_modules"))
        assert standardizer._should_exclude(Path(".DS_Store"))
        assert standardizer._should_exclude(Path("file.pyc"))
        
        # Test non-excluded files
        assert not standardizer._should_exclude(Path("normal_file.txt"))
        assert not standardizer._should_exclude(Path("my_directory"))
    
    def test_should_exclude_custom_patterns(self):
        """Test exclusion of custom patterns."""
        standardizer = FileStandardizer(exclude_patterns=["*.tmp", "backup_*"])
        
        assert standardizer._should_exclude(Path("temp.tmp"))
        assert standardizer._should_exclude(Path("backup_file.txt"))
        assert not standardizer._should_exclude(Path("normal.txt"))
    
    def test_apply_case_style_snake(self):
        """Test snake_case conversion."""
        standardizer = FileStandardizer(case_style="snake")
        
        assert standardizer._apply_case_style("Hello World") == "hello_world"
        assert standardizer._apply_case_style("My-File Name") == "my_file_name"
        assert standardizer._apply_case_style("CamelCase") == "camelcase"
        assert standardizer._apply_case_style("multiple   spaces") == "multiple_spaces"
        assert standardizer._apply_case_style("Special!@#Characters") == "specialcharacters"
    
    def test_apply_case_style_kebab(self):
        """Test kebab-case conversion."""
        standardizer = FileStandardizer(case_style="kebab")
        
        assert standardizer._apply_case_style("Hello World") == "hello-world"
        assert standardizer._apply_case_style("My_File Name") == "my-file-name"
        assert standardizer._apply_case_style("CamelCase") == "camelcase"
    
    def test_apply_case_style_camel(self):
        """Test camelCase conversion."""
        standardizer = FileStandardizer(case_style="camel")
        
        assert standardizer._apply_case_style("hello world") == "helloWorld"
        assert standardizer._apply_case_style("my file name") == "myFileName"
        assert standardizer._apply_case_style("single") == "single"
    
    def test_apply_case_style_pascal(self):
        """Test PascalCase conversion."""
        standardizer = FileStandardizer(case_style="pascal")
        
        assert standardizer._apply_case_style("hello world") == "HelloWorld"
        assert standardizer._apply_case_style("my file name") == "MyFileName"
        assert standardizer._apply_case_style("single") == "Single"
    
    def test_apply_case_style_lower(self):
        """Test lowercase conversion."""
        standardizer = FileStandardizer(case_style="lower")
        
        assert standardizer._apply_case_style("Hello World") == "hello world"
        assert standardizer._apply_case_style("UPPERCASE") == "uppercase"
    
    def test_apply_case_style_upper(self):
        """Test uppercase conversion."""
        standardizer = FileStandardizer(case_style="upper")
        
        assert standardizer._apply_case_style("hello world") == "HELLO WORLD"
        assert standardizer._apply_case_style("lowercase") == "LOWERCASE"
    
    def test_normalize_name_file_with_extension(self):
        """Test normalization of files with extensions."""
        standardizer = FileStandardizer(case_style="snake")
        
        assert standardizer._normalize_name("My File.TXT", is_file=True) == "my_file.txt"
        assert standardizer._normalize_name("Photo IMG_001.JPG", is_file=True) == "photo_img_001.jpg"
        assert standardizer._normalize_name("document.PDF", is_file=True) == "document.pdf"
    
    def test_normalize_name_file_without_extension(self):
        """Test normalization of files without extensions."""
        standardizer = FileStandardizer(case_style="snake")
        
        assert standardizer._normalize_name("My File", is_file=True) == "my_file"
        assert standardizer._normalize_name("README", is_file=True) == "readme"
    
    def test_normalize_name_directory(self):
        """Test normalization of directory names."""
        standardizer = FileStandardizer(case_style="snake")
        
        assert standardizer._normalize_name("My Directory", is_file=False) == "my_directory"
        assert standardizer._normalize_name("Source Code Files", is_file=False) == "source_code_files"


class TestNameChange:
    """Test cases for NameChange dataclass."""
    
    def test_name_change_creation(self):
        """Test creation of NameChange object."""
        old_path = Path("/test/old_name.txt")
        new_path = Path("/test/new_name.txt")
        parent_path = Path("/test")
        
        change = NameChange(
            old_path=old_path,
            new_path=new_path,
            old_name="old_name.txt",
            new_name="new_name.txt",
            parent_path=parent_path,
            is_directory=False
        )
        
        assert change.old_path == old_path
        assert change.new_path == new_path
        assert change.old_name == "old_name.txt"
        assert change.new_name == "new_name.txt"
        assert change.parent_path == parent_path
        assert change.is_directory is False 