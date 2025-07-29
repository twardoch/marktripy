# this_file: tests/test_benchmark.py
"""Performance benchmarks for marktripy."""

import pytest
from pathlib import Path

from marktripy.core.parser import ParserRegistry
from marktripy.parsers.markdown_it import MarkdownItParser  # Import to register
from marktripy.renderers.html import HTMLRenderer
from marktripy.transformers.heading import normalize_headings
from marktripy.transformers.id_generator import add_heading_ids
from marktripy.transformers.toc import generate_toc


# Sample Markdown documents of various sizes
TINY_DOC = """# Title

This is a paragraph.

- List item 1
- List item 2
"""

SMALL_DOC = """# Main Title

## Introduction

This is the introduction paragraph with **bold** and *italic* text.

### Background

Here's some background information with a [link](https://example.com).

## Methods

1. First step
2. Second step
3. Third step

### Data Collection

We collected data using the following approach:

- Survey questionnaires
- Interviews
- Observations

## Results

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

## Conclusion

This is the conclusion.
"""

# Generate a large document
LARGE_DOC_SECTIONS = []
for i in range(50):
    section = f"""## Section {i+1}

This is paragraph {i+1} with some **bold** and *italic* text. Here's a [link](https://example{i}.com).

### Subsection {i+1}.1

- List item 1 in section {i+1}
- List item 2 in section {i+1}
- List item 3 in section {i+1}

### Subsection {i+1}.2

```python
def function_{i}():
    return {i}
```

"""
    LARGE_DOC_SECTIONS.append(section)

LARGE_DOC = "# Large Document\n\n" + "\n".join(LARGE_DOC_SECTIONS)


class TestParsingPerformance:
    """Benchmark parsing performance."""

    @pytest.mark.benchmark(group="parsing")
    def test_parse_tiny_document(self, benchmark):
        """Benchmark parsing a tiny document."""
        parser = ParserRegistry.create("markdown-it")
        result = benchmark(parser.parse, TINY_DOC)
        assert result is not None
        assert len(result.children) > 0

    @pytest.mark.benchmark(group="parsing")
    def test_parse_small_document(self, benchmark):
        """Benchmark parsing a small document."""
        parser = ParserRegistry.create("markdown-it")
        result = benchmark(parser.parse, SMALL_DOC)
        assert result is not None
        assert len(result.children) > 0

    @pytest.mark.benchmark(group="parsing")
    def test_parse_large_document(self, benchmark):
        """Benchmark parsing a large document."""
        parser = ParserRegistry.create("markdown-it")
        result = benchmark(parser.parse, LARGE_DOC)
        assert result is not None
        assert len(result.children) > 0


class TestRenderingPerformance:
    """Benchmark rendering performance."""

    def setup_method(self):
        """Parse documents once for rendering tests."""
        parser = ParserRegistry.create("markdown-it")
        self.tiny_ast = parser.parse(TINY_DOC)
        self.small_ast = parser.parse(SMALL_DOC)
        self.large_ast = parser.parse(LARGE_DOC)

    @pytest.mark.benchmark(group="rendering")
    def test_render_tiny_document(self, benchmark):
        """Benchmark rendering a tiny document."""
        renderer = HTMLRenderer()
        result = benchmark(renderer.render, self.tiny_ast)
        assert result is not None
        assert len(result) > 0

    @pytest.mark.benchmark(group="rendering")
    def test_render_small_document(self, benchmark):
        """Benchmark rendering a small document."""
        renderer = HTMLRenderer()
        result = benchmark(renderer.render, self.small_ast)
        assert result is not None
        assert len(result) > 0

    @pytest.mark.benchmark(group="rendering")
    def test_render_large_document(self, benchmark):
        """Benchmark rendering a large document."""
        renderer = HTMLRenderer()
        result = benchmark(renderer.render, self.large_ast)
        assert result is not None
        assert len(result) > 0


class TestTransformerPerformance:
    """Benchmark transformer performance."""

    def setup_method(self):
        """Parse documents once for transformer tests."""
        parser = ParserRegistry.create("markdown-it")
        self.small_ast = parser.parse(SMALL_DOC)
        self.large_ast = parser.parse(LARGE_DOC)

    @pytest.mark.benchmark(group="transformers")
    def test_normalize_headings_small(self, benchmark):
        """Benchmark normalizing headings in a small document."""
        # Clone AST to avoid modifying the original
        ast = self.small_ast.clone()
        result = benchmark(normalize_headings, ast)
        assert result is not None

    @pytest.mark.benchmark(group="transformers")
    def test_normalize_headings_large(self, benchmark):
        """Benchmark normalizing headings in a large document."""
        ast = self.large_ast.clone()
        result = benchmark(normalize_headings, ast)
        assert result is not None

    @pytest.mark.benchmark(group="transformers")
    def test_add_heading_ids_small(self, benchmark):
        """Benchmark adding heading IDs in a small document."""
        ast = self.small_ast.clone()
        result = benchmark(add_heading_ids, ast)
        assert result is not None

    @pytest.mark.benchmark(group="transformers")
    def test_add_heading_ids_large(self, benchmark):
        """Benchmark adding heading IDs in a large document."""
        ast = self.large_ast.clone()
        result = benchmark(add_heading_ids, ast)
        assert result is not None

    @pytest.mark.benchmark(group="transformers")
    def test_generate_toc_small(self, benchmark):
        """Benchmark generating TOC for a small document."""
        ast = self.small_ast.clone()
        # Add IDs first
        ast = add_heading_ids(ast)
        result = benchmark(generate_toc, ast, max_level=3, insert=False)
        assert result is not None

    @pytest.mark.benchmark(group="transformers")
    def test_generate_toc_large(self, benchmark):
        """Benchmark generating TOC for a large document."""
        ast = self.large_ast.clone()
        # Add IDs first
        ast = add_heading_ids(ast)
        result = benchmark(generate_toc, ast, max_level=3, insert=False)
        assert result is not None


class TestEndToEndPerformance:
    """Benchmark end-to-end workflows."""

    @pytest.mark.benchmark(group="end-to-end")
    def test_parse_transform_render_small(self, benchmark):
        """Benchmark complete workflow for a small document."""
        def workflow():
            # Parse
            parser = ParserRegistry.create("markdown-it")
            ast = parser.parse(SMALL_DOC)
            
            # Transform
            ast = normalize_headings(ast)
            ast = add_heading_ids(ast)
            ast = generate_toc(ast)
            
            # Render
            renderer = HTMLRenderer()
            html = renderer.render(ast)
            
            return html
        
        result = benchmark(workflow)
        assert result is not None
        assert "<h1" in result  # Should have headings
        assert "<ul" in result or "<ol" in result  # Should have lists

    @pytest.mark.benchmark(group="end-to-end")
    def test_parse_transform_render_large(self, benchmark):
        """Benchmark complete workflow for a large document."""
        def workflow():
            # Parse
            parser = ParserRegistry.create("markdown-it")
            ast = parser.parse(LARGE_DOC)
            
            # Transform
            ast = normalize_headings(ast)
            ast = add_heading_ids(ast)
            ast = generate_toc(ast)
            
            # Render
            renderer = HTMLRenderer()
            html = renderer.render(ast)
            
            return html
        
        result = benchmark(workflow)
        assert result is not None
        assert len(result) > 10000  # Should be a large HTML document