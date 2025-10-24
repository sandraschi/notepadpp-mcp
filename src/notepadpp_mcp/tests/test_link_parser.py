"""Tests for link parser module.

This module tests the link parsing functionality to achieve coverage
for the currently untested link_parser.py module.
"""

import re
from unittest.mock import patch

import pytest

from notepadpp_mcp.link_parser import (
    LinkParser,
    LinkParseError,
    LinkParseResult,
    LinkType,
)


class TestLinkParser:
    """Test LinkParser functionality."""

    def test_init(self):
        """Test LinkParser initialization."""
        parser = LinkParser()
        assert parser is not None
        assert hasattr(parser, "parse_links")

    def test_parse_links_empty_text(self):
        """Test parsing links in empty text."""
        parser = LinkParser()

        result = parser.parse_links("")
        assert isinstance(result, LinkParseResult)
        assert len(result.links) == 0
        assert result.total_links == 0

    def test_parse_links_no_links(self):
        """Test parsing text with no links."""
        parser = LinkParser()

        text = "This is just plain text with no links."
        result = parser.parse_links(text)

        assert isinstance(result, LinkParseResult)
        assert len(result.links) == 0
        assert result.total_links == 0

    def test_parse_links_http_links(self):
        """Test parsing HTTP links."""
        parser = LinkParser()

        text = "Visit https://example.com for more info."
        result = parser.parse_links(text)

        assert isinstance(result, LinkParseResult)
        assert len(result.links) == 1
        assert result.total_links == 1
        assert result.links[0].url == "https://example.com"
        assert result.links[0].link_type == LinkType.HTTP

    def test_parse_links_https_links(self):
        """Test parsing HTTPS links."""
        parser = LinkParser()

        text = "Secure site: https://secure.example.com"
        result = parser.parse_links(text)

        assert isinstance(result, LinkParseResult)
        assert len(result.links) == 1
        assert result.links[0].url == "https://secure.example.com"
        assert result.links[0].link_type == LinkType.HTTPS

    def test_parse_links_file_links(self):
        """Test parsing file links."""
        parser = LinkParser()

        text = "Open file:///C:/path/to/file.txt"
        result = parser.parse_links(text)

        assert isinstance(result, LinkParseResult)
        assert len(result.links) == 1
        assert result.links[0].url == "file:///C:/path/to/file.txt"
        assert result.links[0].link_type == LinkType.FILE

    def test_parse_links_mailto_links(self):
        """Test parsing mailto links."""
        parser = LinkParser()

        text = "Email: mailto:test@example.com"
        result = parser.parse_links(text)

        assert isinstance(result, LinkParseResult)
        assert len(result.links) == 1
        assert result.links[0].url == "mailto:test@example.com"
        assert result.links[0].link_type == LinkType.MAILTO

    def test_parse_links_multiple_links(self):
        """Test parsing multiple links."""
        parser = LinkParser()

        text = """
        Visit https://example.com and https://another.com
        Also check file:///C:/test.txt
        Email: mailto:test@example.com
        """
        result = parser.parse_links(text)

        assert isinstance(result, LinkParseResult)
        assert len(result.links) == 4
        assert result.total_links == 4

    def test_parse_links_mixed_content(self):
        """Test parsing links in mixed content."""
        parser = LinkParser()

        text = """
        This is a paragraph with https://example.com link.
        Another paragraph with file:///C:/test.txt file link.
        And a mailto:test@example.com email link.
        """
        result = parser.parse_links(text)

        assert isinstance(result, LinkParseResult)
        assert len(result.links) == 3
        assert result.total_links == 3

    def test_parse_links_invalid_urls(self):
        """Test parsing with invalid URLs."""
        parser = LinkParser()

        text = "Invalid: http:// and https://incomplete"
        result = parser.parse_links(text)

        assert isinstance(result, LinkParseResult)
        # Should not parse incomplete URLs
        assert len(result.links) == 0

    def test_parse_links_with_positions(self):
        """Test parsing links with position information."""
        parser = LinkParser()

        text = "Start https://example.com middle https://test.com end"
        result = parser.parse_links(text)

        assert isinstance(result, LinkParseResult)
        assert len(result.links) == 2

        # Check that positions are captured
        first_link = result.links[0]
        assert first_link.url == "https://example.com"
        assert hasattr(first_link, "start_pos") or hasattr(first_link, "end_pos")

    def test_parse_links_case_insensitive(self):
        """Test parsing links case insensitive."""
        parser = LinkParser()

        text = "HTTPS://EXAMPLE.COM and HTTP://TEST.COM"
        result = parser.parse_links(text)

        assert isinstance(result, LinkParseResult)
        assert len(result.links) == 2

    def test_parse_links_special_characters(self):
        """Test parsing links with special characters."""
        parser = LinkParser()

        text = "https://example.com/path?query=value&other=123"
        result = parser.parse_links(text)

        assert isinstance(result, LinkParseResult)
        assert len(result.links) == 1
        assert result.links[0].url == "https://example.com/path?query=value&other=123"

    def test_parse_links_unicode(self):
        """Test parsing links with Unicode characters."""
        parser = LinkParser()

        text = "https://example.com/测试 and https://example.com/тест"
        result = parser.parse_links(text)

        assert isinstance(result, LinkParseResult)
        assert len(result.links) == 2

    def test_parse_links_nested_content(self):
        """Test parsing links in nested content."""
        parser = LinkParser()

        text = """
        <div>
            <p>Visit https://example.com</p>
            <a href="https://another.com">Link</a>
        </div>
        """
        result = parser.parse_links(text)

        assert isinstance(result, LinkParseResult)
        assert len(result.links) == 2


class TestLinkParseResult:
    """Test LinkParseResult class."""

    def test_link_parse_result_init(self):
        """Test LinkParseResult initialization."""
        result = LinkParseResult()
        assert result.links == []
        assert result.total_links == 0

    def test_link_parse_result_with_links(self):
        """Test LinkParseResult with links."""
        from notepadpp_mcp.link_parser import LinkInfo

        links = [
            LinkInfo("https://example.com", LinkType.HTTP),
            LinkInfo("https://test.com", LinkType.HTTPS),
        ]

        result = LinkParseResult(links)
        assert len(result.links) == 2
        assert result.total_links == 2

    def test_link_parse_result_str(self):
        """Test string representation of LinkParseResult."""
        result = LinkParseResult()
        str_repr = str(result)
        assert "LinkParseResult" in str_repr or "links" in str_repr.lower()

    def test_link_parse_result_repr(self):
        """Test repr of LinkParseResult."""
        result = LinkParseResult()
        repr_str = repr(result)
        assert "LinkParseResult" in repr_str


class TestLinkInfo:
    """Test LinkInfo class."""

    def test_link_info_init(self):
        """Test LinkInfo initialization."""
        from notepadpp_mcp.link_parser import LinkInfo

        link = LinkInfo("https://example.com", LinkType.HTTP)
        assert link.url == "https://example.com"
        assert link.link_type == LinkType.HTTP

    def test_link_info_str(self):
        """Test string representation of LinkInfo."""
        from notepadpp_mcp.link_parser import LinkInfo

        link = LinkInfo("https://example.com", LinkType.HTTP)
        str_repr = str(link)
        assert "https://example.com" in str_repr

    def test_link_info_repr(self):
        """Test repr of LinkInfo."""
        from notepadpp_mcp.link_parser import LinkInfo

        link = LinkInfo("https://example.com", LinkType.HTTP)
        repr_str = repr(link)
        assert "LinkInfo" in repr_str
        assert "https://example.com" in repr_str


class TestLinkType:
    """Test LinkType enum."""

    def test_link_type_values(self):
        """Test LinkType enum values."""
        assert LinkType.HTTP == "http"
        assert LinkType.HTTPS == "https"
        assert LinkType.FILE == "file"
        assert LinkType.MAILTO == "mailto"

    def test_link_type_str(self):
        """Test LinkType string representation."""
        assert str(LinkType.HTTP) == "http"
        assert str(LinkType.HTTPS) == "https"
        assert str(LinkType.FILE) == "file"
        assert str(LinkType.MAILTO) == "mailto"


class TestLinkParseError:
    """Test LinkParseError exception."""

    def test_link_parse_error_init(self):
        """Test LinkParseError initialization."""
        error = LinkParseError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_link_parse_error_with_context(self):
        """Test LinkParseError with context."""
        error = LinkParseError("Test error", context="test context")
        assert str(error) == "Test error"
        assert hasattr(error, "context")
        assert error.context == "test context"


class TestLinkParserEdgeCases:
    """Test edge cases and error conditions."""

    def test_parse_links_none_input(self):
        """Test parsing with None input."""
        parser = LinkParser()

        with pytest.raises((TypeError, AttributeError)):
            parser.parse_links(None)

    def test_parse_links_non_string_input(self):
        """Test parsing with non-string input."""
        parser = LinkParser()

        with pytest.raises((TypeError, AttributeError)):
            parser.parse_links(123)

    def test_parse_links_very_long_text(self):
        """Test parsing with very long text."""
        parser = LinkParser()

        # Create very long text with links
        long_text = "https://example.com " * 10000
        result = parser.parse_links(long_text)

        assert isinstance(result, LinkParseResult)
        assert len(result.links) == 10000

    def test_parse_links_malformed_urls(self):
        """Test parsing with malformed URLs."""
        parser = LinkParser()

        text = "http://[invalid and https://incomplete"
        result = parser.parse_links(text)

        assert isinstance(result, LinkParseResult)
        # Should handle malformed URLs gracefully
        assert len(result.links) == 0

    def test_parse_links_regex_error(self):
        """Test parsing with regex error."""
        parser = LinkParser()

        # Mock re.findall to raise an exception
        with patch("re.findall", side_effect=re.error("Invalid regex")):
            with pytest.raises(LinkParseError):
                parser.parse_links("https://example.com")

    def test_parse_links_memory_error(self):
        """Test parsing with memory error."""
        parser = LinkParser()

        # Create text that might cause memory issues
        text = "https://example.com " * 1000000

        # This should not raise an exception, but might be slow
        result = parser.parse_links(text)
        assert isinstance(result, LinkParseResult)
