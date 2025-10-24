"""
Tests for robust link parser.

Tests all the edge cases that could crash link parsing:
- Very large notes (> 1 MB)
- Many links (> 1000)
- Malformed link syntax
- Catastrophic regex backtracking
- Nested/complex patterns
"""

import pytest
import time
from src.notepadpp_mcp.link_parser import LinkParser, parse_links_safe


class TestBasicLinkParsing:
    """Test basic link parsing functionality."""

    def test_wikilinks(self):
        """Test wikilink parsing."""
        content = "Link to [[Page1]] and [[Page2|Display Text]]."

        parser = LinkParser()
        result = parser.parse_links(content)

        assert result.is_valid
        assert len(result.links) == 2
        assert result.links[0].type == "wikilink"
        assert result.links[0].target == "Page1"
        assert result.links[1].target == "Page2"
        assert result.links[1].text == "Display Text"

    def test_markdown_links(self):
        """Test markdown link parsing."""
        content = (
            "Check [Google](https://google.com) and [Example](http://example.org)."
        )

        parser = LinkParser()
        result = parser.parse_links(content)

        assert result.is_valid
        markdown_links = [link for link in result.links if link.type == "markdown"]
        assert len(markdown_links) == 2
        assert markdown_links[0].text == "Google"
        assert markdown_links[0].target == "https://google.com"

    def test_images(self):
        """Test image link parsing."""
        content = "![Alt text](image.png) and ![](no-alt.jpg)"

        parser = LinkParser()
        result = parser.parse_links(content)

        assert result.is_valid
        images = [link for link in result.links if link.type == "image"]
        assert len(images) == 2
        assert images[0].text == "Alt text"
        assert images[0].target == "image.png"

    def test_raw_urls(self):
        """Test raw URL extraction (when enabled)."""
        content = "Visit https://example.com for more info."

        parser = LinkParser(extract_urls=True)
        result = parser.parse_links(content)

        assert result.is_valid
        urls = [link for link in result.links if link.type == "url"]
        assert len(urls) == 1
        assert urls[0].target == "https://example.com"

    def test_mixed_links(self):
        """Test parsing multiple link types together."""
        content = """
# Document

Visit [[WikiPage]] or check [Google](https://google.com).

![Image](test.png)

Raw URL: https://example.com
"""

        parser = LinkParser(extract_urls=True)
        result = parser.parse_links(content)

        assert result.is_valid
        assert len(result.links) >= 4  # wiki, markdown, image, url

        groups = parser.group_by_type(result.links)
        assert "wikilink" in groups
        assert "markdown" in groups
        assert "image" in groups
        assert "url" in groups


class TestLargeContent:
    """Test handling of very large content."""

    def test_many_wikilinks(self):
        """Test parsing many wikilinks (stress test)."""
        # Generate 5000 links
        links = [f"[[Page{i}]]" for i in range(5000)]
        content = " ".join(links)

        parser = LinkParser()
        result = parser.parse_links(content)

        assert result.is_valid
        assert len(result.links) <= parser.max_links

        if len(result.links) >= parser.WARN_LINK_COUNT:
            assert any("links" in w.lower() for w in result.warnings)

    def test_max_links_limit(self):
        """Test that link limit is enforced."""
        # Generate more links than the limit
        links = [f"[[Page{i}]]" for i in range(15000)]
        content = " ".join(links)

        parser = LinkParser(max_links=1000)
        result = parser.parse_links(content)

        assert result.is_valid  # Doesn't fail, just stops
        assert len(result.links) == 1000  # Limited
        assert any("maximum" in w.lower() for w in result.warnings)

    def test_very_large_file(self):
        """Test handling of very large files."""
        # Generate ~5 MB of content
        large_content = "# Test\n\n" + ("Some text with [[Link]]. " * 100000)

        parser = LinkParser()
        result = parser.parse_links(large_content)

        # Should complete without crashing
        assert result.is_valid or len(result.errors) > 0

    def test_content_size_limit(self):
        """Test rejection of too-large content."""
        # Create content larger than limit
        huge_content = "x" * (11 * 1024 * 1024)  # 11 MB

        parser = LinkParser(max_content_size=10 * 1024 * 1024)
        result = parser.parse_links(huge_content)

        assert not result.is_valid
        assert any("too large" in e.lower() for e in result.errors)


class TestMalformedLinks:
    """Test handling of malformed link syntax."""

    def test_unclosed_wikilink(self):
        """Test unclosed wikilink brackets."""
        content = "This [[Link is never closed."

        parser = LinkParser()
        result = parser.parse_links(content)

        # Should not crash, just find no links
        assert result.is_valid
        assert len(result.links) == 0

    def test_nested_brackets(self):
        """Test nested bracket patterns."""
        content = "[[Outer [[Inner]] Link]]"

        parser = LinkParser()
        result = parser.parse_links(content)

        # Non-greedy regex should handle this
        assert result.is_valid

    def test_malformed_markdown_link(self):
        """Test malformed markdown link."""
        content = "[Text without URL]"

        parser = LinkParser()
        result = parser.parse_links(content)

        # Should not crash, just find no links
        assert result.is_valid
        assert len(result.links) == 0

    def test_incomplete_markdown_link(self):
        """Test incomplete markdown link."""
        content = "[Text](incomplete"

        parser = LinkParser()
        result = parser.parse_links(content)

        # Should not crash
        assert result.is_valid

    def test_empty_links(self):
        """Test empty link patterns."""
        content = "[[]] and []()"

        parser = LinkParser()
        result = parser.parse_links(content)

        # Might match, might not - just shouldn't crash
        assert result.is_valid


class TestCatastrophicBacktracking:
    """Test patterns that could cause catastrophic backtracking."""

    @pytest.mark.timeout(10)
    def test_nested_brackets_stress(self):
        """Test deeply nested brackets."""
        # Create pathological pattern
        content = "[" * 100 + "text" + "]" * 100

        parser = LinkParser()
        start = time.time()
        result = parser.parse_links(content)
        elapsed = time.time() - start

        # Should complete quickly (non-greedy regex)
        assert elapsed < 2.0  # Should be instant
        assert result.is_valid

    @pytest.mark.timeout(10)
    def test_alternating_brackets(self):
        """Test alternating bracket patterns."""
        content = "[[]]" * 1000

        parser = LinkParser()
        start = time.time()
        result = parser.parse_links(content)
        elapsed = time.time() - start

        assert elapsed < 2.0
        assert result.is_valid

    @pytest.mark.timeout(10)
    def test_complex_nested_pattern(self):
        """Test complex nested patterns."""
        content = "[[Link1]] [Link2](" + ("a" * 1000) + ")"

        parser = LinkParser()
        result = parser.parse_links(content)

        # Should handle without timeout
        assert result.is_valid


class TestPerformance:
    """Test parsing performance."""

    def test_parse_time_tracking(self):
        """Test that parse time is tracked."""
        content = "[[Link1]] and [[Link2]]"

        parser = LinkParser()
        result = parser.parse_links(content)

        assert result.parse_time_ms > 0
        assert result.parse_time_ms < 1000  # Should be < 1 second

    @pytest.mark.timeout(10)
    def test_timeout_enforcement(self):
        """Test that parsing timeout is enforced."""
        # Create content that takes a while to parse
        links = [f"[[Page{i}]]" for i in range(100000)]
        content = " ".join(links)

        parser = LinkParser(max_parse_time=1.0)  # 1 second timeout
        result = parser.parse_links(content)

        # Should either complete or timeout, but not hang
        assert result.is_valid or any("timeout" in e.lower() for e in result.errors)

    def test_small_file_performance(self):
        """Test that small files parse quickly."""
        content = "# Test\n\nSome text with [[Link1]] and [Link2](url)."

        parser = LinkParser()
        start = time.time()
        result = parser.parse_links(content)
        elapsed = time.time() - start

        assert elapsed < 0.1  # Should be instant
        assert result.is_valid


class TestStatistics:
    """Test link statistics generation."""

    def test_get_statistics(self):
        """Test statistics generation."""
        content = """
[[Wiki1]] [[Wiki2]]
[Markdown](url1) [Text](url2)
![Image](img1.png)
https://example.com
"""

        parser = LinkParser(extract_urls=True)
        result = parser.parse_links(content)
        stats = parser.get_statistics(result)

        assert stats["total_links"] > 0
        assert "wikilinks" in stats
        assert "markdown_links" in stats
        assert "images" in stats
        assert "parse_time_ms" in stats

    def test_unique_targets(self):
        """Test unique target extraction."""
        content = "[[Page1]] [[Page1]] [[Page2]]"

        parser = LinkParser()
        result = parser.parse_links(content)
        unique = parser.extract_unique_targets(result.links)

        assert len(unique) == 2  # Page1, Page2
        assert "Page1" in unique
        assert "Page2" in unique

    def test_group_by_type(self):
        """Test grouping links by type."""
        content = "[[Wiki]] [Markdown](url) ![Image](img)"

        parser = LinkParser()
        result = parser.parse_links(content)
        groups = parser.group_by_type(result.links)

        assert "wikilink" in groups
        assert "markdown" in groups
        assert "image" in groups
        assert len(groups["wikilink"]) == 1


class TestSafeWrapper:
    """Test safe parsing wrapper."""

    def test_safe_parse_success(self):
        """Test safe parse on valid content."""
        content = "[[Link]]"

        result = parse_links_safe(content)

        assert result.is_valid
        assert len(result.links) == 1

    def test_safe_parse_on_error(self):
        """Test safe parse handles errors gracefully."""
        # Even if parsing fails, should return valid result
        content = "x" * (20 * 1024 * 1024)  # 20 MB

        result = parse_links_safe(content)

        # Should not crash, returns result with errors
        assert isinstance(result.links, list)


class TestEdgeCases:
    """Test various edge cases."""

    def test_empty_content(self):
        """Test parsing empty content."""
        parser = LinkParser()
        result = parser.parse_links("")

        assert result.is_valid
        assert len(result.links) == 0

    def test_no_links(self):
        """Test content with no links."""
        content = "# Title\n\nJust some regular text."

        parser = LinkParser()
        result = parser.parse_links(content)

        assert result.is_valid
        assert len(result.links) == 0

    def test_only_whitespace(self):
        """Test content with only whitespace."""
        content = "   \n\n\t\t  \n  "

        parser = LinkParser()
        result = parser.parse_links(content)

        assert result.is_valid
        assert len(result.links) == 0

    def test_unicode_in_links(self):
        """Test unicode characters in links."""
        content = "[[日本語ページ]] and [Café](http://café.com)"

        parser = LinkParser()
        result = parser.parse_links(content)

        assert result.is_valid
        assert len(result.links) == 2


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
