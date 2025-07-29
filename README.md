# marktripy

**TL;DR**: A Python package for parsing Markdown to AST, manipulating the tree structure, and serializing back to Markdown while preserving formatting. Built on `markdown-it-py` and `mistletoe` for maximum flexibility.

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

## Installation

```bash
# Using pip
pip install marktripy

# Using uv (recommended)
uv add marktripy

# Development installation
git clone https://github.com/yourusername/marktripy
cd marktripy
uv sync --dev
```

## Quick Usage

### Basic Markdown to HTML

```python
from marktripy import markdown_to_html

html = markdown_to_html("# Hello World\n\nThis is **bold** and *italic*.")
# <h1>Hello World</h1><p>This is <strong>bold</strong> and <em>italic</em>.</p>
```

### AST Manipulation

```python
from marktripy import parse_markdown, render_markdown

# Parse Markdown to AST
ast = parse_markdown("""
# Main Title
## Section 1
Some content here.
## Section 2
More content.
""")

# Add IDs to all headings
for node in ast.walk():
    if node.type == "heading":
        # Generate ID from heading text
        text = node.get_text().lower().replace(" ", "-")
        node.attrs["id"] = text
        
# Downgrade all headings by one level
for node in ast.walk():
    if node.type == "heading" and node.level < 6:
        node.level += 1

# Render back to Markdown
result = render_markdown(ast)
```

### Custom Syntax Extensions

```python
from marktripy import create_extension, Parser

# Create a custom extension for ++text++ → <kbd>text</kbd>
kbd_extension = create_extension(
    pattern=r'\+\+([^+]+)\+\+',
    node_type='kbd',
    html_tag='kbd'
)

# Use parser with extension
parser = Parser(extensions=[kbd_extension])
ast = parser.parse("Press ++Ctrl+C++ to copy")
html = parser.render_html(ast)
# Output: Press <kbd>Ctrl+C</kbd> to copy
```

### CLI Usage

```bash
# Convert Markdown to HTML
marktripy convert input.md -o output.html

# Parse and manipulate Markdown
marktripy transform input.md --downgrade-headings --add-ids -o output.md

# Validate Markdown structure
marktripy validate document.md --check-links --check-headings
```

## The Backstory

### Why Another Markdown Parser?

The Python ecosystem has numerous Markdown parsers, each with different strengths:

- **`markdown`**: The original, extensible but with a complex API
- **`markdown2`**: Faster alternative but less extensible
- **`mistune`**: Fast and supports AST, but limited round-trip capability
- **`marko`**: Good AST support but newer with less ecosystem
- **`markdown-it-py`**: Port of markdown-it with excellent plugin system

After extensive research (see `/ref` directory), I found that no single library perfectly addressed the need for:

1. **Clean AST manipulation** - Easy traversal and modification of document structure
2. **Round-trip conversion** - Parse Markdown → AST → Markdown without losing formatting
3. **Extensibility** - Simple API for adding custom syntax
4. **Performance** - Fast enough for real-world documents
5. **Standards compliance** - CommonMark compliant with GFM extensions

### The Research Journey

The `/ref` directory contains comprehensive research comparing 8+ Python Markdown libraries across multiple dimensions:

- **ref1.md**: Practical guide to advanced Markdown processing in Python
- **ref2.md**: Detailed comparison of parser architectures and extension mechanisms
- **ref3.md**: Performance benchmarks and feature matrix

Key findings:

- `markdown-it-py` offers the best plugin architecture
- `mistletoe` has the cleanest AST representation
- `marko` provides good round-trip capabilities
- Performance varies by 10-100x between libraries

### Design Philosophy

`marktripy` combines the best ideas from existing libraries:

1. **Dual-parser architecture**: Use `markdown-it-py` for extensibility and `mistletoe` for AST manipulation
2. **Unified AST format**: Convert between parser representations transparently
3. **Preserving formatting**: Track source positions and whitespace for faithful round-trips
4. **Plugin-first design**: Everything beyond core CommonMark is a plugin
5. **Type safety**: Full type hints with `mypy --strict` compatibility

## Technical Architecture

### Core Components

```text
marktripy/
├── ast.py          # Unified AST node definitions
├── parser.py       # Parser abstraction layer
├── renderer.py     # Markdown/HTML renderers
├── extensions/     # Built-in extensions
│   ├── gfm.py     # GitHub Flavored Markdown
│   ├── toc.py     # Table of contents generator
│   └── ...
├── transformers/   # AST transformation utilities
│   ├── headings.py # Heading manipulation
│   ├── links.py    # Link processing
│   └── ...
└── cli.py         # Command-line interface
```

### AST Structure

The AST uses a unified node structure compatible with both parsers:

```python
class ASTNode:
    type: str           # Node type (heading, paragraph, etc.)
    children: List[ASTNode]
    attrs: Dict[str, Any]   # Attributes (id, class, etc.)
    content: str        # Text content for leaf nodes
    meta: Dict[str, Any]    # Source mapping, parser-specific data
```

### Parser Architecture

```python
# Abstraction layer over multiple parsers
class Parser:
    def __init__(self, parser_backend="markdown-it-py", extensions=None):
        self.backend = self._create_backend(parser_backend)
        self.extensions = extensions or []
        
    def parse(self, markdown: str) -> ASTNode:
        # Parse with backend
        backend_ast = self.backend.parse(markdown)
        # Convert to unified AST
        return self._normalize_ast(backend_ast)
```

### Extension System

Extensions can hook into multiple stages:

```python
class Extension:
    def extend_parser(self, parser): ...      # Modify parser rules
    def transform_ast(self, ast): ...         # Post-process AST
    def extend_renderer(self, renderer): ...  # Custom rendering
```

### Rendering Pipeline

1. **AST → Markdown**: Preserves formatting, handles custom nodes
2. **AST → HTML**: Configurable sanitization, custom handlers
3. **AST → JSON**: Serialization for processing pipelines

### Performance Optimizations

- Lazy parsing for large documents
- Streaming renderers for memory efficiency  
- Optional C extensions via `umarkdown` backend
- Caching for repeated transformations

## Advanced Usage

### Custom Transformers

```python
from marktripy import Transformer

class HeaderAnchorTransformer(Transformer):
    """Add GitHub-style anchor links to headers"""
    
    def transform(self, ast):
        for node in ast.walk():
            if node.type == "heading":
                anchor = self.create_anchor(node)
                node.children.insert(0, anchor)
        return ast
```

### Parser Backends

```python
# Use different backends for different needs
from marktripy import Parser

# Maximum compatibility
parser = Parser(backend="markdown")

# Best performance  
parser = Parser(backend="mistletoe")

# Most extensions
parser = Parser(backend="markdown-it-py")
```

### Integration Examples

```python
# Pelican static site generator
from marktripy import PelicanReader

# MkDocs documentation
from marktripy import MkDocsPlugin

# Jupyter notebook processing
from marktripy import MarkdownCell
```

## Contributing

We welcome contributions! Key areas:

- Additional extensions (math, diagrams, etc.)
- Performance improvements
- Better round-trip fidelity
- More transformer utilities

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Built on the shoulders of giants:

- `markdown-it-py` developers for the excellent plugin system
- `mistletoe` for the clean AST design
- The CommonMark specification authors
- All researchers of the Python Markdown ecosystem
