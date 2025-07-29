# this_file: tests/test_transformers.py
"""Tests for AST transformers."""

import pytest

from marktripy.core.ast import Document, Heading, Link, List, ListItem, Paragraph, Text
from marktripy.core.parser import ParserRegistry
from marktripy.core.validator import validate_ast
from marktripy.parsers.markdown_it import MarkdownItParser  # Import to register
from marktripy.transformers.heading import (
    HeadingNormalizer,
    decrease_heading_levels,
    increase_heading_levels,
    normalize_headings,
)
from marktripy.transformers.id_generator import add_heading_ids, add_ids_to_elements
from marktripy.transformers.link_reference import collect_links, convert_to_reference_links
from marktripy.transformers.toc import extract_toc, generate_toc


class TestHeadingTransformer:
    """Test heading level transformations."""

    def test_increase_heading_levels(self):
        """Test increasing heading levels."""
        # Create document with headings
        doc = Document()
        h1 = Heading(level=1)
        h1.add_child(Text(content="Title"))
        h2 = Heading(level=2)
        h2.add_child(Text(content="Section"))
        h3 = Heading(level=3)
        h3.add_child(Text(content="Subsection"))

        doc.add_child(h1)
        doc.add_child(h2)
        doc.add_child(h3)

        # Increase levels
        result = increase_heading_levels(doc, amount=2)

        # Check results
        headings = result.find_all("heading")
        assert len(headings) == 3
        assert headings[0].level == 3
        assert headings[1].level == 4
        assert headings[2].level == 5

    def test_decrease_heading_levels(self):
        """Test decreasing heading levels."""
        # Create document
        doc = Document()
        doc.add_child(Heading(level=3))
        doc.add_child(Heading(level=4))
        doc.add_child(Heading(level=5))

        # Decrease levels
        result = decrease_heading_levels(doc, amount=2)

        # Check results
        headings = result.find_all("heading")
        assert headings[0].level == 1  # Clamped to minimum
        assert headings[1].level == 2
        assert headings[2].level == 3

    def test_normalize_headings(self):
        """Test normalizing heading hierarchy."""
        # Create document with gaps in heading levels
        doc = Document()
        h2 = Heading(level=2)
        h2.add_child(Text(content="First"))
        h4 = Heading(level=4)
        h4.add_child(Text(content="Second"))
        h6 = Heading(level=6)
        h6.add_child(Text(content="Third"))
        h4_2 = Heading(level=4)
        h4_2.add_child(Text(content="Fourth"))

        doc.add_child(h2)
        doc.add_child(h4)
        doc.add_child(h6)
        doc.add_child(h4_2)

        # Normalize
        result = normalize_headings(doc)

        # Check results - should be 1, 2, 3, 2
        headings = result.find_all("heading")
        assert headings[0].level == 1  # 2 -> 1
        assert headings[1].level == 2  # 4 -> 2
        assert headings[2].level == 3  # 6 -> 3
        assert headings[3].level == 2  # 4 -> 2

    def test_heading_transformer_with_parser(self):
        """Test heading transformer with parsed content."""
        parser = ParserRegistry.create("markdown-it")
        ast = parser.parse(
            """
# Main Title
## Section 1
### Subsection 1.1
## Section 2
"""
        )

        # Normalize headings
        normalizer = HeadingNormalizer()
        result = normalizer.transform(ast)

        # Validate and check
        errors = validate_ast(result)
        assert len(errors) == 0

        headings = result.find_all("heading")
        assert len(headings) == 4
        assert all(1 <= h.level <= 6 for h in headings)


class TestIDGenerator:
    """Test ID generation for elements."""

    def test_add_heading_ids(self):
        """Test adding IDs to headings."""
        # Create document
        doc = Document()
        h1 = Heading(level=1)
        h1.add_child(Text(content="Hello World"))
        h2 = Heading(level=2)
        h2.add_child(Text(content="Test Section"))
        h2_dup = Heading(level=2)
        h2_dup.add_child(Text(content="Test Section"))

        doc.add_child(h1)
        doc.add_child(h2)
        doc.add_child(h2_dup)

        # Add IDs
        result = add_heading_ids(doc)

        # Check IDs
        headings = result.find_all("heading")
        assert headings[0].get_attr("id") == "hello-world"
        assert headings[1].get_attr("id") == "test-section"
        assert headings[2].get_attr("id") == "test-section-1"  # Duplicate handling

    def test_preserve_existing_ids(self):
        """Test that existing IDs are preserved."""
        doc = Document()
        h1 = Heading(level=1)
        h1.add_child(Text(content="Title"))
        h1.set_attr("id", "custom-id")
        h2 = Heading(level=2)
        h2.add_child(Text(content="Section"))

        doc.add_child(h1)
        doc.add_child(h2)

        # Add IDs without overwriting
        result = add_heading_ids(doc, overwrite=False)

        headings = result.find_all("heading")
        assert headings[0].get_attr("id") == "custom-id"  # Preserved
        assert headings[1].get_attr("id") == "section"  # Generated

    def test_id_prefix(self):
        """Test ID generation with prefix."""
        doc = Document()
        h1 = Heading(level=1)
        h1.add_child(Text(content="Title"))
        doc.add_child(h1)

        result = add_heading_ids(doc, prefix="section")

        heading = result.find_all("heading")[0]
        assert heading.get_attr("id") == "section-title"

    def test_add_ids_to_multiple_elements(self):
        """Test adding IDs to different element types."""
        from marktripy.core.ast import Table, TableRow, TableCell

        doc = Document()
        h1 = Heading(level=1)
        h1.add_child(Text(content="Title"))
        
        # Create table with content
        table = Table()
        row = TableRow()
        cell = TableCell()
        cell.add_child(Text(content="Data Table"))
        row.add_child(cell)
        table.add_child(row)
        
        doc.add_child(h1)
        doc.add_child(table)

        # Add IDs to both headings and tables
        result = add_ids_to_elements(doc, ["heading", "table"])

        assert result.find_all("heading")[0].get_attr("id") == "title"
        assert result.find_all("table")[0].get_attr("id") == "data-table"


class TestLinkReference:
    """Test link reference transformations."""

    def test_collect_links(self):
        """Test collecting all links in document."""
        doc = Document()
        p1 = Paragraph()
        link1 = Link(href="https://example.com", title="Example")
        link1.add_child(Text(content="Example Site"))
        p1.add_child(link1)

        p2 = Paragraph()
        link2 = Link(href="https://github.com")
        link2.add_child(Text(content="GitHub"))
        p2.add_child(link2)

        doc.add_child(p1)
        doc.add_child(p2)

        # Collect links
        links = collect_links(doc)
        assert len(links) == 2
        assert links[0].href == "https://example.com"
        assert links[1].href == "https://github.com"

    def test_convert_to_reference_links_numeric(self):
        """Test converting inline links to numeric references."""
        doc = Document()
        p = Paragraph()
        link1 = Link(href="https://example.com")
        link1.add_child(Text(content="Example"))
        link2 = Link(href="https://github.com")
        link2.add_child(Text(content="GitHub"))
        link3 = Link(href="https://example.com")  # Duplicate
        link3.add_child(Text(content="Example Again"))

        p.add_child(link1)
        p.add_child(Text(content=" and "))
        p.add_child(link2)
        p.add_child(Text(content=" and "))
        p.add_child(link3)
        doc.add_child(p)

        # Convert to references
        result = convert_to_reference_links(doc, style="numeric", dedup=True)

        # Check that links have reference IDs
        links = collect_links(result)
        assert links[0].get_attr("reference_id") == "1"
        assert links[1].get_attr("reference_id") == "2"
        assert links[2].get_attr("reference_id") == "1"  # Reused due to dedup

        # Check reference section was added
        # Last children should be reference paragraphs
        last_paras = [
            child for child in result.children[-3:] if child.type == "paragraph"
        ]
        assert len(last_paras) >= 2  # At least 2 unique URLs

    def test_convert_to_reference_links_text(self):
        """Test converting inline links to text-based references."""
        doc = Document()
        p = Paragraph()
        link = Link(href="https://example.com")
        link.add_child(Text(content="Example Site"))
        p.add_child(link)
        doc.add_child(p)

        # Convert with text style
        result = convert_to_reference_links(doc, style="text")

        links = collect_links(result)
        ref_id = links[0].get_attr("reference_id")
        assert ref_id == "example-site"


class TestTOCGenerator:
    """Test table of contents generation."""

    def test_generate_basic_toc(self):
        """Test generating a simple TOC."""
        doc = Document()
        h1 = Heading(level=1)
        h1.add_child(Text(content="Introduction"))
        h2_1 = Heading(level=2)
        h2_1.add_child(Text(content="Background"))
        h2_2 = Heading(level=2)
        h2_2.add_child(Text(content="Methods"))
        h3 = Heading(level=3)
        h3.add_child(Text(content="Data Collection"))

        doc.add_child(h1)
        doc.add_child(h2_1)
        doc.add_child(h2_2)
        doc.add_child(h3)

        # First add IDs to headings
        doc_with_ids = add_heading_ids(doc)

        # Generate TOC
        result = generate_toc(doc_with_ids, max_level=3, insert=False)

        # Extract TOC separately
        toc = extract_toc(doc_with_ids, max_level=3)
        assert toc is not None

        # Check TOC structure
        toc_items = toc.find_all("list_item")
        assert len(toc_items) >= 3  # At least 3 headings included

    def test_toc_with_max_level(self):
        """Test TOC respects max level setting."""
        doc = Document()
        for level in range(1, 7):
            h = Heading(level=level)
            h.add_child(Text(content=f"Level {level}"))
            doc.add_child(h)

        doc_with_ids = add_heading_ids(doc)
        toc = extract_toc(doc_with_ids, max_level=3)

        # Should only include levels 1-3
        toc_links = toc.find_all("link") if toc else []
        assert len(toc_links) == 3

    def test_toc_insertion(self):
        """Test inserting TOC into document."""
        parser = ParserRegistry.create("markdown-it")
        ast = parser.parse(
            """
# Document Title

[[TOC]]

## Section 1
### Subsection 1.1

## Section 2
"""
        )

        # Add IDs first
        ast_with_ids = add_heading_ids(ast)

        # Generate and insert TOC
        result = generate_toc(ast_with_ids, max_level=3, insert=True)

        # Check that TOC was inserted
        # Should have more nodes than original due to TOC
        assert len(result.find_all("list")) > 0

    def test_toc_with_links(self):
        """Test that TOC entries link to headings."""
        doc = Document()
        h1 = Heading(level=1)
        h1.add_child(Text(content="Main"))
        h1.set_attr("id", "main")
        h2 = Heading(level=2)
        h2.add_child(Text(content="Sub"))
        h2.set_attr("id", "sub")

        doc.add_child(h1)
        doc.add_child(h2)

        toc = extract_toc(doc)
        links = toc.find_all("link") if toc else []

        assert len(links) == 2
        assert links[0].href == "#main"
        assert links[1].href == "#sub"


class TestTransformerIntegration:
    """Test combining multiple transformers."""

    def test_transform_pipeline(self):
        """Test applying multiple transformers in sequence."""
        parser = ParserRegistry.create("markdown-it")
        ast = parser.parse(
            """
## Introduction

This is a [link](https://example.com) to an example.

### Background

More content with [another link](https://github.com).

## Methods

Final section.
"""
        )

        # Apply transformers in sequence
        # 1. Normalize headings
        ast = normalize_headings(ast)

        # 2. Add IDs
        ast = add_heading_ids(ast)

        # 3. Generate TOC
        ast = generate_toc(ast, max_level=2)

        # 4. Convert links to references
        ast = convert_to_reference_links(ast)

        # Validate final result
        errors = validate_ast(ast)
        assert len(errors) == 0

        # Check all transformations were applied
        headings = ast.find_all("heading")
        assert headings[0].level == 1  # Normalized
        assert headings[0].get_attr("id") is not None  # Has ID

        links = collect_links(ast)
        assert all(link.get_attr("reference_id") is not None for link in links)

        # TOC should be present
        lists = ast.find_all("list")
        assert len(lists) > 0  # At least one list (the TOC)