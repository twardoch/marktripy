# this_file: tests/test_roundtrip.py
"""Round-trip conversion tests for marktripy."""

import pytest

from marktripy.core.parser import ParserRegistry
from marktripy.parsers.markdown_it import MarkdownItParser  # Import to register
from marktripy.parsers.mistletoe_parser import MistletoeParser  # Import to register
from marktripy.renderers.html import HTMLRenderer
from marktripy.renderers.markdown import MarkdownRenderer


class TestBasicRoundTrip:
    """Test basic round-trip conversions."""

    @pytest.mark.parametrize("parser_name", ["markdown-it", "mistletoe"])
    def test_simple_paragraph(self, parser_name):
        """Test round-trip for simple paragraph."""
        original = "This is a simple paragraph."
        
        parser = ParserRegistry.create(parser_name)
        renderer = MarkdownRenderer()
        
        ast = parser.parse(original)
        result = renderer.render(ast)
        
        assert result.strip() == original

    @pytest.mark.parametrize("parser_name", ["markdown-it", "mistletoe"])
    def test_headings(self, parser_name):
        """Test round-trip for headings."""
        original = """# Heading 1

## Heading 2

### Heading 3"""
        
        parser = ParserRegistry.create(parser_name)
        renderer = MarkdownRenderer()
        
        ast = parser.parse(original)
        result = renderer.render(ast)
        
        assert result.strip() == original

    def test_emphasis_variations(self):
        """Test different emphasis styles."""
        test_cases = [
            ("*italic*", "*italic*"),
            ("_italic_", "*italic*"),  # Normalized to *
            ("**bold**", "**bold**"),
            ("__bold__", "**bold**"),  # Normalized to **
            ("***bold italic***", "***bold italic***"),
        ]
        
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer()
        
        for original, expected in test_cases:
            ast = parser.parse(original)
            result = renderer.render(ast)
            assert result.strip() == expected

    def test_lists(self):
        """Test round-trip for lists."""
        original = """- Item 1
- Item 2
- Item 3

1. First
2. Second
3. Third"""
        
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer()
        
        ast = parser.parse(original)
        result = renderer.render(ast)
        
        # Normalize whitespace for comparison
        assert result.strip() == original

    def test_nested_lists(self):
        """Test round-trip for nested lists."""
        original = """- Item 1
   - Nested 1
   - Nested 2
- Item 2"""
        
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer()
        
        ast = parser.parse(original)
        result = renderer.render(ast)
        
        # Check structure is preserved
        lines = result.strip().split("\n")
        assert len(lines) == 4
        assert lines[0] == "- Item 1"
        assert "   -" in lines[1]  # Nested item

    def test_code_blocks(self):
        """Test round-trip for code blocks."""
        original = '''```python
def hello():
    print("Hello, World!")
```'''
        
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer()
        
        ast = parser.parse(original)
        result = renderer.render(ast)
        
        assert result.strip() == original

    def test_inline_code(self):
        """Test round-trip for inline code."""
        original = "Use `print()` function to display output."
        
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer()
        
        ast = parser.parse(original)
        result = renderer.render(ast)
        
        assert result.strip() == original

    def test_links(self):
        """Test round-trip for links."""
        test_cases = [
            "[Google](https://google.com)",
            '[Example](https://example.com "Example Title")',
        ]
        
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer()
        
        for original in test_cases:
            ast = parser.parse(original)
            result = renderer.render(ast)
            assert result.strip() == original

    def test_images(self):
        """Test round-trip for images."""
        test_cases = [
            "![Alt text](image.png)",
            '![Logo](logo.png "Company Logo")',
        ]
        
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer()
        
        for original in test_cases:
            ast = parser.parse(original)
            result = renderer.render(ast)
            assert result.strip() == original

    def test_blockquotes(self):
        """Test round-trip for blockquotes."""
        original = """> This is a quote
> with multiple lines
>
> And a new paragraph"""
        
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer()
        
        ast = parser.parse(original)
        result = renderer.render(ast)
        
        # Check structure
        lines = result.strip().split("\n")
        assert all(line.startswith(">") or line == "" for line in lines)

    def test_horizontal_rules(self):
        """Test round-trip for horizontal rules."""
        test_cases = ["---", "***", "___"]
        
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer()
        
        for original in test_cases:
            ast = parser.parse(original)
            result = renderer.render(ast)
            # All normalize to ---
            assert result.strip() == "---"


class TestComplexRoundTrip:
    """Test round-trip for complex documents."""

    def test_mixed_content(self):
        """Test round-trip for document with mixed content."""
        original = """# Title

This is a paragraph with **bold** and *italic* text.

## Lists

- Item 1
- Item 2
  - Nested item
- Item 3

## Code

Here's some `inline code` and a block:

```python
def example():
    return "Hello"
```

## Quote

> This is a quote
> with multiple lines"""
        
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer()
        
        ast = parser.parse(original)
        result = renderer.render(ast)
        
        # Check major sections are preserved
        assert "# Title" in result
        assert "## Lists" in result
        assert "## Code" in result
        assert "## Quote" in result
        assert "**bold**" in result
        assert "*italic*" in result
        assert "```python" in result

    def test_table_roundtrip(self):
        """Test round-trip for tables."""
        original = """| Header 1 | Header 2 |
| -------- | -------- |
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |"""
        
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer()
        
        ast = parser.parse(original)
        result = renderer.render(ast)
        
        # Check table structure
        lines = result.strip().split("\n")
        assert len(lines) == 4
        assert "|" in lines[0]  # Header
        assert "-" in lines[1]  # Separator
        assert "|" in lines[2]  # Data row
        assert "|" in lines[3]  # Data row

    def test_escaped_characters(self):
        """Test round-trip for escaped characters."""
        # Note: The renderer escapes special chars, so we test the concept
        original = "This has special chars: \\* \\_ \\` \\[ \\]"
        
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer()
        
        ast = parser.parse(original)
        result = renderer.render(ast)
        
        # Should preserve the escaped nature
        assert "\\*" in result
        assert "\\_" in result


class TestParserComparison:
    """Compare round-trip behavior between parsers."""

    def test_parser_consistency(self):
        """Test that both parsers produce similar ASTs."""
        test_docs = [
            "# Simple Heading",
            "This is a **bold** statement.",
            "- List item 1\n- List item 2",
            "[Link](https://example.com)",
            "> Blockquote text",
        ]
        
        for doc in test_docs:
            # Parse with both parsers
            parser1 = ParserRegistry.create("markdown-it")
            parser2 = ParserRegistry.create("mistletoe")
            
            ast1 = parser1.parse(doc)
            ast2 = parser2.parse(doc)
            
            # Render both ASTs
            renderer = MarkdownRenderer()
            result1 = renderer.render(ast1)
            result2 = renderer.render(ast2)
            
            # Results should be very similar (might have minor differences)
            assert result1.strip() == result2.strip()


class TestRenderingOptions:
    """Test different rendering options."""

    def test_setext_headings(self):
        """Test rendering with setext-style headings."""
        original = "# Heading 1\n\n## Heading 2\n\n### Heading 3"
        
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer({"heading_style": "setext"})
        
        ast = parser.parse(original)
        result = renderer.render(ast)
        
        lines = result.strip().split("\n")
        # H1 and H2 should be setext style
        assert "===" in result  # H1 underline
        assert "---" in result  # H2 underline
        assert "###" in result  # H3 stays ATX

    def test_custom_emphasis_chars(self):
        """Test rendering with custom emphasis characters."""
        original = "*italic* and **bold**"
        
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer({
            "emphasis_char": "_",
            "strong_char": "__"
        })
        
        ast = parser.parse(original)
        result = renderer.render(ast)
        
        assert "_italic_" in result
        assert "__bold__" in result

    def test_custom_bullet_char(self):
        """Test rendering with custom bullet character."""
        original = "- Item 1\n- Item 2"
        
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer({"bullet_char": "*"})
        
        ast = parser.parse(original)
        result = renderer.render(ast)
        
        assert result.startswith("* Item 1")
        assert "* Item 2" in result


class TestEdgeCases:
    """Test edge cases in round-trip conversion."""

    def test_empty_document(self):
        """Test round-trip for empty document."""
        original = ""
        
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer()
        
        ast = parser.parse(original)
        result = renderer.render(ast)
        
        assert result.strip() == original

    def test_whitespace_only(self):
        """Test round-trip for whitespace-only document."""
        original = "   \n\n   "
        
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer()
        
        ast = parser.parse(original)
        result = renderer.render(ast)
        
        # Should normalize to empty
        assert result.strip() == ""

    def test_special_characters_in_code(self):
        """Test special characters in code blocks."""
        original = '''```
Special chars: * _ ` [ ] ( ) # + - . !
```'''
        
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer()
        
        ast = parser.parse(original)
        result = renderer.render(ast)
        
        # Code content should be preserved
        assert "* _ `" in result

    def test_nested_emphasis(self):
        """Test nested emphasis structures."""
        original = "***bold and italic***"
        
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer()
        
        ast = parser.parse(original)
        result = renderer.render(ast)
        
        # Should preserve the nested structure
        assert "***" in result or "**_" in result or "_**" in result