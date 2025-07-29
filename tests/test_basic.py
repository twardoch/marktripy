# this_file: tests/test_basic.py
"""Basic tests for marktripy functionality."""

import pytest

from marktripy.core.ast import Document, Heading, Paragraph, Text
from marktripy.core.parser import ParserRegistry
from marktripy.parsers.markdown_it import MarkdownItParser
from marktripy.renderers.base import RendererRegistry
from marktripy.renderers.html import HTMLRenderer


class TestBasicFunctionality:
    """Test basic marktripy functionality."""

    def test_parser_registration(self):
        """Test that parser can be registered and retrieved."""
        # Parser should be auto-registered on import
        parser_class = ParserRegistry.get("markdown-it")
        assert parser_class is MarkdownItParser

        # Should be able to create instance
        parser = ParserRegistry.create("markdown-it")
        assert isinstance(parser, MarkdownItParser)

    def test_renderer_registration(self):
        """Test that renderer can be registered and retrieved."""
        # Renderer should be auto-registered on import
        renderer_class = RendererRegistry.get("html")
        assert renderer_class is HTMLRenderer

        # Should be able to create instance
        renderer = RendererRegistry.create("html")
        assert isinstance(renderer, HTMLRenderer)

    def test_simple_markdown_parsing(self):
        """Test parsing simple Markdown text."""
        parser = MarkdownItParser()

        markdown = "# Hello World\n\nThis is a paragraph."
        doc = parser.parse(markdown)

        # Check document structure
        assert isinstance(doc, Document)
        assert len(doc.children) == 2

        # Check heading
        heading = doc.children[0]
        assert isinstance(heading, Heading)
        assert heading.level == 1
        assert len(heading.children) == 1
        assert isinstance(heading.children[0], Text)
        assert heading.children[0].content == "Hello World"

        # Check paragraph
        para = doc.children[1]
        assert isinstance(para, Paragraph)
        assert len(para.children) == 1
        assert isinstance(para.children[0], Text)
        assert para.children[0].content == "This is a paragraph."

    def test_html_rendering(self):
        """Test rendering AST to HTML."""
        # Create simple AST
        doc = Document()
        heading = Heading(level=1)
        heading.add_child(Text("Hello World"))
        doc.add_child(heading)

        para = Paragraph()
        para.add_child(Text("This is a paragraph."))
        doc.add_child(para)

        # Render to HTML
        renderer = HTMLRenderer()
        html = renderer.render(doc)

        assert "<h1>Hello World</h1>" in html
        assert "<p>This is a paragraph.</p>" in html

    def test_parse_and_render_pipeline(self):
        """Test full pipeline: parse Markdown to AST to HTML."""
        parser = MarkdownItParser()
        renderer = HTMLRenderer()

        markdown = """# Main Title

This is a **bold** paragraph with *italic* text.

## Subtitle

- Item 1
- Item 2
- Item 3

Here's some `inline code` and a [link](https://example.com).
"""

        # Parse to AST
        doc = parser.parse(markdown)

        # Render to HTML
        html = renderer.render(doc)

        # Check HTML output
        assert "<h1>Main Title</h1>" in html
        assert "<strong>bold</strong>" in html
        assert "<em>italic</em>" in html
        assert "<h2>Subtitle</h2>" in html
        assert "<ul>" in html
        assert "<li>Item 1</li>" in html
        assert "<code>inline code</code>" in html
        assert '<a href="https://example.com">link</a>' in html

    def test_code_block_rendering(self):
        """Test code block parsing and rendering."""
        parser = MarkdownItParser()
        renderer = HTMLRenderer()

        markdown = """```python
def hello():
    print("Hello, world!")
```"""

        doc = parser.parse(markdown)
        html = renderer.render(doc)

        assert "<pre><code" in html
        assert 'class="language-python"' in html
        assert "def hello():" in html
        # Quotes should be escaped in HTML
        assert "print(&quot;Hello, world!&quot;)" in html

    def test_nested_structures(self):
        """Test parsing and rendering nested structures."""
        parser = MarkdownItParser()
        renderer = HTMLRenderer()

        markdown = """
> ## Quote Title
>
> This is a quoted paragraph with **bold** text.
>
> 1. First item
> 2. Second item
"""

        doc = parser.parse(markdown)
        html = renderer.render(doc)

        assert "<blockquote>" in html
        assert "<h2>Quote Title</h2>" in html
        assert "<ol>" in html
        assert "<li>First item</li>" in html

    def test_html_escaping(self):
        """Test that HTML special characters are escaped."""
        parser = MarkdownItParser()
        renderer = HTMLRenderer()

        markdown = 'This has <script>alert("XSS")</script> & special chars.'

        doc = parser.parse(markdown)
        html = renderer.render(doc)

        assert "&lt;script&gt;" in html
        assert "&quot;XSS&quot;" in html
        assert "&amp;" in html
        assert "<script>" not in html  # Should be escaped


class TestASTManipulation:
    """Test AST manipulation functionality."""

    def test_node_traversal(self):
        """Test AST node traversal methods."""
        doc = Document()
        h1 = Heading(level=1)
        h1.add_child(Text("Title"))
        doc.add_child(h1)

        para = Paragraph()
        para.add_child(Text("Some "))
        para.add_child(Text("text"))
        doc.add_child(para)

        # Test walk method
        all_nodes = doc.walk()
        assert len(all_nodes) == 6  # doc, h1, text in h1, para, 2 texts in para

        # Test find_all method
        text_nodes = doc.find_all("text")
        assert len(text_nodes) == 3
        assert all(node.type == "text" for node in text_nodes)

    def test_node_manipulation(self):
        """Test adding, removing, and replacing nodes."""
        para = Paragraph()
        text1 = Text("Hello")
        text2 = Text(" ")
        text3 = Text("World")

        # Test adding
        para.add_child(text1)
        para.add_child(text2)
        para.add_child(text3)
        assert len(para.children) == 3

        # Test removing
        para.remove_child(text2)
        assert len(para.children) == 2
        assert para.children == [text1, text3]

        # Test replacing
        new_text = Text("Python")
        para.replace_child(text3, new_text)
        assert para.children == [text1, new_text]

    def test_node_attributes(self):
        """Test node attribute management."""
        heading = Heading(level=2)

        # Test setting and getting attributes
        heading.set_attr("id", "my-heading")
        heading.set_attr("class", "special")

        assert heading.get_attr("id") == "my-heading"
        assert heading.get_attr("class") == "special"
        assert heading.get_attr("missing", "default") == "default"

    def test_node_cloning(self):
        """Test deep cloning of nodes."""
        doc = Document()
        para = Paragraph()
        para.add_child(Text("Original"))
        para.set_attr("id", "original")
        doc.add_child(para)

        # Clone the document
        cloned = doc.clone()

        # Verify structure is copied
        assert len(cloned.children) == 1
        assert isinstance(cloned.children[0], Paragraph)
        assert cloned.children[0].get_attr("id") == "original"
        assert cloned.children[0].children[0].content == "Original"

        # Verify it's a deep copy
        cloned.children[0].children[0].content = "Modified"
        assert para.children[0].content == "Original"  # Original unchanged


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
