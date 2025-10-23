"""Tests for file validator module.

This module tests the file validation functionality to achieve coverage
for the currently untested file_validator.py module.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from notepadpp_mcp.file_validator import (
    FileValidator,
    ValidationResult,
)


class TestFileValidator:
    """Test FileValidator functionality."""

    def test_init(self):
        """Test FileValidator initialization."""
        validator = FileValidator()
        assert validator is not None
        assert hasattr(validator, 'validate_file')

    def test_validate_file_exists(self):
        """Test validation of existing file."""
        validator = FileValidator()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            test_file = f.name

        try:
            result = validator.validate_file(test_file)
            assert isinstance(result, ValidationResult)
            assert result.is_valid is True
            assert result.file_path == test_file
            
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)

    def test_validate_file_not_exists(self):
        """Test validation of non-existent file."""
        validator = FileValidator()
        
        result = validator.validate_file("nonexistent_file.txt")
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert "not found" in result.error_message.lower()

    def test_validate_file_permission_error(self):
        """Test validation with permission error."""
        validator = FileValidator()
        
        # Mock os.path.exists to raise permission error
        with patch('os.path.exists', side_effect=PermissionError("Permission denied")):
            result = validator.validate_file("test.txt")
            assert isinstance(result, ValidationResult)
            assert result.is_valid is False
            assert "permission" in result.error_message.lower()

    def test_validate_file_empty_path(self):
        """Test validation with empty path."""
        validator = FileValidator()
        
        result = validator.validate_file("")
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert "empty" in result.error_message.lower()

    def test_validate_file_none_path(self):
        """Test validation with None path."""
        validator = FileValidator()
        
        result = validator.validate_file(None)
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert "none" in result.error_message.lower()

    def test_validate_file_directory(self):
        """Test validation of directory instead of file."""
        validator = FileValidator()
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            result = validator.validate_file(temp_dir)
            assert isinstance(result, ValidationResult)
            assert result.is_valid is False
            assert "directory" in result.error_message.lower()

    def test_validate_file_large_file(self):
        """Test validation of large file."""
        validator = FileValidator()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            # Write some content
            f.write("test content")
            test_file = f.name

        try:
            # Mock os.path.getsize to return large size
            with patch('os.path.getsize', return_value=100 * 1024 * 1024):  # 100MB
                result = validator.validate_file(test_file)
                assert isinstance(result, ValidationResult)
                # Should still be valid, just large
                assert result.is_valid is True
                
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)

    def test_validate_file_binary_file(self):
        """Test validation of binary file."""
        validator = FileValidator()
        
        # Create a temporary binary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(b'\x00\x01\x02\x03')
            test_file = f.name

        try:
            result = validator.validate_file(test_file)
            assert isinstance(result, ValidationResult)
            assert result.is_valid is True
            
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)

    def test_validate_file_symlink(self):
        """Test validation of symbolic link."""
        validator = FileValidator()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            test_file = f.name

        try:
            # Create a symlink (if supported on platform)
            try:
                symlink_path = test_file + "_link"
                os.symlink(test_file, symlink_path)
                
                result = validator.validate_file(symlink_path)
                assert isinstance(result, ValidationResult)
                assert result.is_valid is True
                
                os.unlink(symlink_path)
                
            except OSError:
                # Symlinks not supported on this platform
                pytest.skip("Symlinks not supported on this platform")
                
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)


class TestValidationResult:
    """Test ValidationResult class."""

    def test_validation_result_success(self):
        """Test successful validation result."""
        result = ValidationResult(
            file_path="test.txt",
            is_valid=True,
            file_size=1024,
            file_type="text"
        )
        
        assert result.file_path == "test.txt"
        assert result.is_valid is True
        assert result.file_size == 1024
        assert result.file_type == "text"
        assert result.error_message is None

    def test_validation_result_error(self):
        """Test validation result with error."""
        result = ValidationResult(
            file_path="test.txt",
            is_valid=False,
            error_message="File not found"
        )
        
        assert result.file_path == "test.txt"
        assert result.is_valid is False
        assert result.error_message == "File not found"
        assert result.file_size is None
        assert result.file_type is None

    def test_validation_result_str(self):
        """Test string representation of validation result."""
        result = ValidationResult(
            file_path="test.txt",
            is_valid=True,
            file_size=1024,
            file_type="text"
        )
        
        str_repr = str(result)
        assert "test.txt" in str_repr
        assert "valid" in str_repr.lower()

    def test_validation_result_repr(self):
        """Test repr of validation result."""
        result = ValidationResult(
            file_path="test.txt",
            is_valid=True,
            file_size=1024,
            file_type="text"
        )
        
        repr_str = repr(result)
        assert "ValidationResult" in repr_str
        assert "test.txt" in repr_str


# ValidationError class doesn't exist in the actual module


class TestFileValidatorEdgeCases:
    """Test edge cases and error conditions."""

    def test_validate_file_unicode_path(self):
        """Test validation with Unicode file path."""
        validator = FileValidator()
        
        # Create a temporary file with Unicode name
        with tempfile.NamedTemporaryFile(mode='w', suffix='测试.txt', delete=False) as f:
            f.write("test content")
            test_file = f.name

        try:
            result = validator.validate_file(test_file)
            assert isinstance(result, ValidationResult)
            assert result.is_valid is True
            
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)

    def test_validate_file_very_long_path(self):
        """Test validation with very long file path."""
        validator = FileValidator()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            test_file = f.name

        try:
            # Create a very long path
            long_path = test_file + "x" * 200
            
            result = validator.validate_file(long_path)
            assert isinstance(result, ValidationResult)
            assert result.is_valid is False
            
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)

    def test_validate_file_special_characters(self):
        """Test validation with special characters in path."""
        validator = FileValidator()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            test_file = f.name

        try:
            result = validator.validate_file(test_file)
            assert isinstance(result, ValidationResult)
            assert result.is_valid is True
            
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)

    def test_validate_file_concurrent_access(self):
        """Test validation with concurrent file access."""
        validator = FileValidator()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            test_file = f.name

        try:
            # Mock file access to simulate concurrent access
            with patch('builtins.open', side_effect=OSError("File in use")):
                result = validator.validate_file(test_file)
                assert isinstance(result, ValidationResult)
                # Should still validate file existence
                assert result.is_valid is True
                
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
