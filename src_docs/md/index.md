# marktripy Documentation

## TL;DR

**marktripy** is a Python package for converting Markdown to AST (Abstract Syntax Tree), manipulating the tree structure, and serializing back to Markdown while preserving formatting. Built on `markdown-it-py` and `mistletoe` for maximum flexibility and extensibility.

```python
from marktripy import parse_markdown, render_markdown

# Parse Markdown to AST
ast = parse_markdown("# Hello\n\nThis is **bold** text.")

# Manipulate AST (e.g., downgrade headings)
for node in ast.walk():
    if node.type == "heading":
        node.level += 1

# Render back to Markdown
markdown = render_markdown(ast)
# Output: "## Hello\n\nThis is **bold** text."
```

## What marktripy Does

- **Parse** Markdown documents into a manipulable AST
- **Transform** document structure programmatically  
- **Extend** Markdown syntax with custom elements
- **Preserve** formatting during round-trip conversions
- **Generate** HTML, JSON, and other formats from AST
- **Validate** document structure and links

## Documentation Roadmap

This documentation is organized into 9 comprehensive chapters:

### 1. [Installation](installation.md)
Learn how to install marktripy using pip, uv, or from source. Covers virtual environments, development setup, and dependency management.

### 2. [Quick Start](quickstart.md) 
Get up and running in minutes with basic examples of parsing, manipulating, and rendering Markdown. Perfect for first-time users.

### 3. [Core Concepts](core-concepts.md)
Deep dive into marktripy's architecture: AST structure, parser backends, rendering pipeline, and the unified node system.

### 4. [AST Manipulation](ast-manipulation.md)
Master the art of programmatically modifying document structure: traversing nodes, transforming content, and preserving metadata.

### 5. [Extensions System](extensions.md)
Create custom Markdown syntax extensions: from simple text replacements to complex block-level elements with custom rendering.

### 6. [Transformers](transformers.md)
Use built-in transformers and create your own: heading manipulation, link processing, TOC generation, and content validation.

### 7. [Performance](performance.md)
Optimize for speed and memory: choosing the right parser backend, streaming large documents, and performance benchmarking.

### 8. [CLI Usage](cli.md)
Master the command-line interface: batch processing, validation tools, transformation pipelines, and integration scripts.

### 9. [API Reference](api-reference.md)
Complete API documentation with detailed class and method references, generated from docstrings with examples.

## Why marktripy?

The Python ecosystem has many Markdown parsers, but none perfectly address the need for **clean AST manipulation**, **round-trip conversion**, **extensibility**, and **performance** in one package. 

marktripy combines the best ideas from existing libraries:

- **Dual-parser architecture** for flexibility
- **Unified AST format** for consistency  
- **Plugin-first design** for extensibility
- **Type safety** with full type hints
- **Standards compliance** with CommonMark and GFM

## Quick Navigation

=== "New Users"
    1. [Installation](installation.md) - Get set up
    2. [Quick Start](quickstart.md) - Basic examples
    3. [Core Concepts](core-concepts.md) - Understand the architecture

=== "Developers"
    1. [AST Manipulation](ast-manipulation.md) - Programmatic document editing
    2. [Extensions System](extensions.md) - Custom syntax
    3. [API Reference](api-reference.md) - Complete documentation

=== "Power Users"
    1. [Transformers](transformers.md) - Advanced document processing
    2. [Performance](performance.md) - Optimization techniques
    3. [CLI Usage](cli.md) - Command-line tools

## Getting Help

- **GitHub Issues**: [Report bugs and request features](https://github.com/twardoch/marktripy/issues)
- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/twardoch/marktripy/discussions)
- **Examples**: Check the `/examples` directory in the repository
- **Research**: See `/ref` directory for library comparison and design decisions

## Next Steps

Ready to get started? Head to the [Installation](installation.md) guide to set up marktripy, then try the [Quick Start](quickstart.md) examples to see it in action.

For a deeper understanding of the design philosophy and technical decisions, explore the research documents in the `/ref` directory of the repository.