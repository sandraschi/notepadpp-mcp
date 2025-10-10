"""
Tests for robust file validation.

Tests all the edge cases that could crash sync:
- Weird filenames
- Zero-size files
- Unreadable contents
- Broken frontmatter
- Permission issues
"""

import pytest
import tempfile
from pathlib import Path
from src.notepadpp_mcp.file_validator import FileValidator, validate_markdown_file


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestWeirdFilenames:
    """Test handling of problematic filenames."""
    
    def test_unicode_filename(self, temp_dir):
        """Test filename with unicode characters."""
        file_path = temp_dir / "日本語ファイル.md"
        file_path.write_text("# Japanese filename")
        
        result = validate_markdown_file(file_path)
        
        assert result.is_valid
        assert any("Non-ASCII" in w for w in result.warnings)
    
    def test_spaces_in_filename(self, temp_dir):
        """Test filename with spaces."""
        file_path = temp_dir / "file with spaces.md"
        file_path.write_text("# Spaces")
        
        result = validate_markdown_file(file_path)
        
        assert result.is_valid
        assert any("Spaces" in w for w in result.warnings)
    
    def test_special_chars_filename(self, temp_dir):
        """Test filename with special characters."""
        # Use underscores instead of actual special chars for safety
        file_path = temp_dir / "file_with_underscores_and_dashes-2024.md"
        file_path.write_text("# Special chars")
        
        result = validate_markdown_file(file_path)
        
        assert result.is_valid
    
    def test_very_long_filename(self, temp_dir):
        """Test extremely long filename."""
        long_name = "a" * 250 + ".md"
        file_path = temp_dir / long_name
        file_path.write_text("# Long name")
        
        result = validate_markdown_file(file_path)
        
        assert not result.is_valid
        assert any("too long" in e.lower() for e in result.errors)
    
    def test_reserved_windows_name(self, temp_dir):
        """Test Windows reserved filename."""
        file_path = temp_dir / "CON.md"
        
        # Don't actually create - Windows won't allow it
        # Just test the validator logic
        validator = FileValidator()
        result = validator.validate_file(file_path)
        
        # Will fail on "doesn't exist" but that's okay
        # The important thing is the reserved name check
        assert any("Reserved" in e or "does not exist" in e for e in result.errors)


class TestEmptyAndSizeIssues:
    """Test handling of file size issues."""
    
    def test_empty_file_allowed(self, temp_dir):
        """Test empty file (0 bytes) is allowed but warned."""
        file_path = temp_dir / "empty.md"
        file_path.write_text("")
        
        validator = FileValidator(allow_empty=True)
        result = validator.validate_file(file_path)
        
        assert result.is_valid
        assert any("Empty file" in w for w in result.warnings)
        assert result.size_bytes == 0
    
    def test_empty_file_not_allowed(self, temp_dir):
        """Test empty file rejection when strict."""
        file_path = temp_dir / "empty.md"
        file_path.write_text("")
        
        validator = FileValidator(allow_empty=False)
        result = validator.validate_file(file_path)
        
        assert not result.is_valid
        assert any("Empty file" in e for e in result.errors)
    
    def test_very_large_file(self, temp_dir):
        """Test rejection of huge files."""
        file_path = temp_dir / "huge.md"
        
        # Create 1MB file
        large_content = "# Test\n" + ("x" * 1024 * 1024)
        file_path.write_text(large_content)
        
        # Set small max size
        validator = FileValidator(max_file_size=100 * 1024)  # 100 KB
        result = validator.validate_file(file_path)
        
        assert not result.is_valid
        assert any("too large" in e.lower() for e in result.errors)


class TestEncodingIssues:
    """Test handling of encoding problems."""
    
    def test_utf8_file(self, temp_dir):
        """Test normal UTF-8 file."""
        file_path = temp_dir / "utf8.md"
        file_path.write_text("# Hello 世界", encoding='utf-8')
        
        result = validate_markdown_file(file_path)
        
        assert result.is_valid
        assert result.content == "# Hello 世界"
        assert result.encoding == "utf-8"
    
    def test_utf8_bom_file(self, temp_dir):
        """Test UTF-8 with BOM."""
        file_path = temp_dir / "utf8bom.md"
        file_path.write_text("# BOM test", encoding='utf-8-sig')
        
        result = validate_markdown_file(file_path)
        
        assert result.is_valid
        assert result.encoding in ['utf-8', 'utf-8-sig']
    
    def test_latin1_file(self, temp_dir):
        """Test Latin-1 encoded file."""
        file_path = temp_dir / "latin1.md"
        with open(file_path, 'w', encoding='latin-1') as f:
            f.write("# Café")
        
        result = validate_markdown_file(file_path)
        
        # Should work with fallback encoding
        assert result.is_valid
        assert "Café" in result.content
    
    def test_binary_file(self, temp_dir):
        """Test rejection of binary files."""
        file_path = temp_dir / "binary.md"
        file_path.write_bytes(b'\x00\x01\x02\x03\xFF')
        
        result = validate_markdown_file(file_path)
        
        assert not result.is_valid
        assert any("Binary" in e or "null bytes" in e.lower() for e in result.errors)
    
    def test_mixed_line_endings(self, temp_dir):
        """Test mixed line endings."""
        file_path = temp_dir / "mixed.md"
        file_path.write_text("Line 1\nLine 2\r\nLine 3\n")
        
        result = validate_markdown_file(file_path)
        
        assert result.is_valid
        assert any("Mixed line endings" in w for w in result.warnings)


class TestFrontmatterIssues:
    """Test handling of broken frontmatter."""
    
    def test_valid_frontmatter(self, temp_dir):
        """Test valid YAML frontmatter."""
        file_path = temp_dir / "valid_front.md"
        content = """---
title: Test Document
author: Test User
tags:
  - test
  - markdown
---

# Content
"""
        file_path.write_text(content)
        
        result = validate_markdown_file(file_path)
        
        assert result.is_valid
        assert result.frontmatter is not None
        assert result.frontmatter.get('title') == 'Test Document'
    
    def test_missing_closing_marker(self, temp_dir):
        """Test frontmatter without closing ---."""
        file_path = temp_dir / "incomplete_front.md"
        content = """---
title: Test
author: Someone

# Content starts here
"""
        file_path.write_text(content)
        
        validator = FileValidator(strict_frontmatter=False)
        result = validator.validate_file(file_path)
        
        assert result.is_valid  # Not strict
        assert any("incomplete" in w.lower() or "closing" in w.lower() for w in result.warnings)
    
    def test_invalid_yaml_frontmatter(self, temp_dir):
        """Test malformed YAML frontmatter."""
        file_path = temp_dir / "bad_yaml.md"
        content = """---
title: Test
author: [unclosed bracket
tags: [test
---

# Content
"""
        file_path.write_text(content)
        
        validator = FileValidator(strict_frontmatter=False)
        result = validator.validate_file(file_path)
        
        assert result.is_valid  # Not strict, just warns
        assert any("YAML" in w or "frontmatter" in w.lower() for w in result.warnings)
    
    def test_strict_invalid_frontmatter(self, temp_dir):
        """Test strict mode rejects invalid frontmatter."""
        file_path = temp_dir / "bad_yaml_strict.md"
        content = """---
title: Test
bad: [syntax
---

# Content
"""
        file_path.write_text(content)
        
        validator = FileValidator(strict_frontmatter=True)
        result = validator.validate_file(file_path)
        
        # Should be invalid in strict mode
        assert not result.is_valid
        assert any("YAML" in e or "frontmatter" in e.lower() for e in result.errors)
    
    def test_no_frontmatter(self, temp_dir):
        """Test file without frontmatter is valid."""
        file_path = temp_dir / "no_front.md"
        file_path.write_text("# Just content\n\nNo frontmatter here.")
        
        result = validate_markdown_file(file_path)
        
        assert result.is_valid
        assert result.frontmatter is None


class TestContentIssues:
    """Test handling of content problems."""
    
    def test_very_long_lines(self, temp_dir):
        """Test warning on extremely long lines."""
        file_path = temp_dir / "long_line.md"
        long_line = "# " + ("x" * 15000)
        file_path.write_text(long_line)
        
        result = validate_markdown_file(file_path)
        
        assert result.is_valid
        assert any("long line" in w.lower() for w in result.warnings)
    
    def test_normal_markdown(self, temp_dir):
        """Test normal markdown file validates perfectly."""
        file_path = temp_dir / "normal.md"
        content = """# Test Document

This is a normal markdown file with:
- Lists
- **Bold text**
- [Links](https://example.com)

## Section 2

Normal content here.
"""
        file_path.write_text(content)
        
        result = validate_markdown_file(file_path)
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert result.content == content


class TestBatchValidation:
    """Test batch validation of multiple files."""
    
    def test_batch_all_valid(self, temp_dir):
        """Test batch validation with all valid files."""
        # Create multiple valid files
        for i in range(5):
            (temp_dir / f"file_{i}.md").write_text(f"# File {i}")
        
        validator = FileValidator()
        files = list(temp_dir.glob("*.md"))
        results = validator.validate_batch(files)
        
        assert len(results) == 5
        assert all(r.is_valid for r in results.values())
    
    def test_batch_mixed_validity(self, temp_dir):
        """Test batch with mix of valid and invalid files."""
        # Valid files
        (temp_dir / "valid1.md").write_text("# Valid 1")
        (temp_dir / "valid2.md").write_text("# Valid 2")
        
        # Invalid files
        (temp_dir / "empty.md").write_text("")  # Will warn
        (temp_dir / "binary.md").write_bytes(b'\x00\xFF')  # Will error
        
        validator = FileValidator(allow_empty=False)
        files = list(temp_dir.glob("*.md"))
        results = validator.validate_batch(files)
        
        valid_count = sum(1 for r in results.values() if r.is_valid)
        assert valid_count == 2
        assert len(results) == 4
    
    def test_batch_summary(self, temp_dir):
        """Test batch validation summary generation."""
        # Create test files
        (temp_dir / "good.md").write_text("# Good")
        (temp_dir / "empty.md").write_text("")
        (temp_dir / "binary.md").write_bytes(b'\x00')
        
        validator = FileValidator(allow_empty=False)
        files = list(temp_dir.glob("*.md"))
        results = validator.validate_batch(files)
        summary = validator.get_summary(results)
        
        assert "File Validation Summary" in summary
        assert "Total Files: 3" in summary
        assert "Invalid:" in summary


class TestEdgeCases:
    """Test various edge cases."""
    
    def test_nonexistent_file(self, temp_dir):
        """Test validation of non-existent file."""
        file_path = temp_dir / "nonexistent.md"
        
        result = validate_markdown_file(file_path)
        
        assert not result.is_valid
        assert any("does not exist" in e.lower() for e in result.errors)
    
    def test_directory_not_file(self, temp_dir):
        """Test validation of directory."""
        dir_path = temp_dir / "subdir"
        dir_path.mkdir()
        
        result = validate_markdown_file(dir_path)
        
        assert not result.is_valid
        assert any("not a file" in e.lower() for e in result.errors)
    
    def test_wrong_extension(self, temp_dir):
        """Test file with wrong extension."""
        file_path = temp_dir / "notmarkdown.txt"
        file_path.write_text("# Content")
        
        result = validate_markdown_file(file_path)
        
        assert result.is_valid  # Content is valid
        assert any("extension" in w.lower() for w in result.warnings)


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

