# API Reference

Complete API documentation for marktripy, generated from docstrings with comprehensive examples and usage patterns.

## Core Classes

### Parser

The main entry point for parsing Markdown documents.

```python
class Parser:
    """
    Main parser class for converting Markdown to AST.
    
    Args:
        backend (str): Parser backend to use ('mistletoe', 'markdown-it-py', 'markdown')
        extensions (List[str|Extension]): List of extensions to enable
        options (Dict[str, Any]): Parser-specific options
        auto_discover (bool): Whether to auto-discover installed extensions
    
    Examples:
        >>> parser = Parser(backend='mistletoe', extensions=['gfm'])
        >>> ast = parser.parse("# Hello World")
        >>> html = parser.render_html(ast)
    """
    
    def __init__(self, 
                 backend: str = "markdown-it-py",
                 extensions: List[Union[str, Extension]] = None,
                 options: Dict[str, Any] = None,
                 auto_discover: bool = False):
        """Initialize parser with specified configuration."""
    
    def parse(self, markdown_text: str, **kwargs) -> ASTNode:
        """
        Parse Markdown text into AST.
        
        Args:
            markdown_text (str): Markdown source text
            **kwargs: Additional parsing options
        
        Returns:
            ASTNode: Root AST node
        
        Raises:
            ParseError: If parsing fails
        
        Examples:
            >>> ast = parser.parse("# Hello\n\nSome **bold** text.")
            >>> print(ast.type)  # 'document'
        """
    
    def render_markdown(self, ast: ASTNode, **kwargs) -> str:
        """
        Render AST back to Markdown.
        
        Args:
            ast (ASTNode): AST to render
            **kwargs: Rendering options
        
        Returns:
            str: Rendered Markdown text
        
        Examples:
            >>> markdown = parser.render_markdown(ast)
            >>> print(markdown)
        """
    
    def render_html(self, ast: ASTNode, **kwargs) -> str:
        """
        Render AST to HTML.
        
        Args:
            ast (ASTNode): AST to render
            **kwargs: HTML rendering options
        
        Returns:
            str: Rendered HTML
        
        Examples:
            >>> html = parser.render_html(ast)
            >>> print(html)  # '<h1>Hello</h1><p>Some <strong>bold</strong> text.</p>'
        """
    
    def render_json(self, ast: ASTNode, **kwargs) -> str:
        """
        Render AST to JSON.
        
        Args:
            ast (ASTNode): AST to render
            **kwargs: JSON rendering options (pretty, indent, etc.)
        
        Returns:
            str: JSON representation of AST
        
        Examples:
            >>> json_str = parser.render_json(ast, pretty=True, indent=2)
            >>> import json
            >>> data = json.loads(json_str)
        """
```

### ASTNode

The fundamental building block of marktripy's AST representation.

```python
class ASTNode:
    """
    Represents a node in the Abstract Syntax Tree.
    
    Attributes:
        type (str): Node type (heading, paragraph, text, etc.)
        children (List[ASTNode]): Child nodes
        attrs (Dict[str, Any]): Node attributes (id, class, href, etc.)
        content (str): Text content for leaf nodes
        meta (Dict[str, Any]): Metadata (source position, parser info)
        level (int): Heading level (1-6, for heading nodes only)
    
    Examples:
        >>> node = ASTNode(type="heading", level=1)
        >>> node.children.append(ASTNode(type="text", content="Title"))
        >>> print(node.type)  # 'heading'
    """
    
    def __init__(self, 
                 type: str,
                 children: List['ASTNode'] = None,
                 attrs: Dict[str, Any] = None,
                 content: str = "",
                 meta: Dict[str, Any] = None,
                 **kwargs):
        """Initialize AST node."""
    
    def walk(self) -> Iterator['ASTNode']:
        """
        Walk through all nodes in document order.
        
        Yields:
            ASTNode: Each node in the subtree
        
        Examples:
            >>> for node in ast.walk():
            ...     print(f"Node: {node.type}")
        """
    
    def find(self, node_type: str) -> List['ASTNode']:
        """
        Find all nodes of specified type.
        
        Args:
            node_type (str): Type of nodes to find
        
        Returns:
            List[ASTNode]: Matching nodes
        
        Examples:
            >>> headings = ast.find("heading")
            >>> links = ast.find("link")
        """
    
    def find_by_attrs(self, **attrs) -> List['ASTNode']:
        """
        Find nodes by attribute values.
        
        Args:
            **attrs: Attribute key-value pairs to match
        
        Returns:
            List[ASTNode]: Matching nodes
        
        Examples:
            >>> nodes = ast.find_by_attrs(id="section-1")
            >>> external_links = ast.find_by_attrs(class="external")
        """
    
    def get_text(self) -> str:
        """
        Extract all text content from node and children.
        
        Returns:
            str: Combined text content
        
        Examples:
            >>> text = heading_node.get_text()
            >>> print(text)  # "Section Title"
        """
    
    def copy(self, deep: bool = True) -> 'ASTNode':
        """
        Create a copy of the node.
        
        Args:
            deep (bool): Whether to deep copy children
        
        Returns:
            ASTNode: Copy of the node
        
        Examples:
            >>> node_copy = original_node.copy()
            >>> shallow_copy = original_node.copy(deep=False)
        """
```

## Convenience Functions

### Top-level Functions

```python
def parse_markdown(markdown_text: str, 
                  parser: str = "markdown-it-py",
                  extensions: List[str] = None,
                  **kwargs) -> ASTNode:
    """
    Parse Markdown text using default configuration.
    
    Args:
        markdown_text (str): Markdown source
        parser (str): Parser backend to use
        extensions (List[str]): Extensions to enable
        **kwargs: Additional parser options
    
    Returns:
        ASTNode: Parsed AST
    
    Examples:
        >>> ast = parse_markdown("# Hello World")
        >>> ast = parse_markdown(text, extensions=['gfm', 'kbd'])
    """

def render_markdown(ast: ASTNode, **kwargs) -> str:
    """
    Render AST to Markdown using default renderer.
    
    Args:
        ast (ASTNode): AST to render
        **kwargs: Rendering options
    
    Returns:
        str: Rendered Markdown
    
    Examples:
        >>> markdown = render_markdown(ast)
        >>> formatted = render_markdown(ast, preserve_whitespace=True)
    """

def markdown_to_html(markdown_text: str,
                    parser: str = "markdown-it-py", 
                    extensions: List[str] = None,
                    **kwargs) -> str:
    """
    Convert Markdown directly to HTML.
    
    Args:
        markdown_text (str): Markdown source
        parser (str): Parser backend
        extensions (List[str]): Extensions to enable
        **kwargs: Parser and renderer options
    
    Returns:
        str: HTML output
    
    Examples:
        >>> html = markdown_to_html("# Hello **World**")
        >>> html = markdown_to_html(text, extensions=['gfm'])
    """

def markdown_to_json(markdown_text: str, **kwargs) -> str:
    """
    Convert Markdown to JSON AST representation.
    
    Args:
        markdown_text (str): Markdown source
        **kwargs: Parser options
    
    Returns:
        str: JSON representation
    
    Examples:
        >>> json_ast = markdown_to_json("# Hello")
        >>> data = json.loads(json_ast)
    """
```

## Extensions

### Extension Base Classes

```python
class BaseExtension:
    """
    Base class for marktripy extensions.
    
    Attributes:
        name (str): Extension name
        priority (int): Processing priority (lower = earlier)
    
    Examples:
        >>> class MyExtension(BaseExtension):
        ...     name = "my_extension"
        ...     def transform_ast(self, ast):
        ...         return ast
    """
    
    name: str = None
    priority: int = 100
    
    def extend_parser(self, parser) -> None:
        """
        Extend parser with new rules.
        
        Args:
            parser: Parser instance to extend
        
        Examples:
            >>> def extend_parser(self, parser):
            ...     parser.add_rule("my_syntax", my_rule_function)
        """
    
    def transform_ast(self, ast: ASTNode) -> ASTNode:
        """
        Transform AST after parsing.
        
        Args:
            ast (ASTNode): AST to transform
        
        Returns:
            ASTNode: Transformed AST
        
        Examples:
            >>> def transform_ast(self, ast):
            ...     for node in ast.walk():
            ...         if node.type == "text":
            ...             node.content = node.content.upper()
            ...     return ast
        """
    
    def extend_renderer(self, renderer) -> None:
        """
        Add custom rendering rules.
        
        Args:
            renderer: Renderer instance to extend
        
        Examples:
            >>> def extend_renderer(self, renderer):
            ...     renderer.add_rule("my_node", self.render_my_node)
        """
```

### Built-in Extensions

```python
class GFMExtension(BaseExtension):
    """
    GitHub Flavored Markdown extension.
    
    Enables:
        - Strikethrough (~~text~~)
        - Tables
        - Task lists
        - Autolinks
    
    Examples:
        >>> parser = Parser(extensions=['gfm'])
        >>> parser = Parser(extensions=[GFMExtension()])
    """

class KbdExtension(BaseExtension):
    """
    Keyboard shortcut extension.
    
    Converts ++key++ to <kbd>key</kbd>
    
    Args:
        pattern (str): Custom regex pattern
        html_tag (str): HTML tag to use (default: 'kbd')
    
    Examples:
        >>> ext = KbdExtension()
        >>> parser = Parser(extensions=[ext])
        >>> # ++Ctrl+C++ becomes <kbd>Ctrl+C</kbd>
    """

class MathExtension(BaseExtension):
    """
    Mathematical expressions extension.
    
    Supports:
        - Inline math: $equation$
        - Block math: $$equation$$
    
    Args:
        renderer (str): Math renderer ('katex', 'mathjax')
        inline_delimiter (str): Inline math delimiter
        block_delimiter (str): Block math delimiter
    
    Examples:
        >>> ext = MathExtension(renderer='katex')
        >>> parser = Parser(extensions=[ext])
    """
```

## Transformers

### Transformer Base Classes

```python
class BaseTransformer:
    """
    Base class for AST transformers.
    
    Examples:
        >>> class MyTransformer(BaseTransformer):
        ...     def transform(self, ast):
        ...         # Apply transformations
        ...         return ast
    """
    
    def transform(self, ast: ASTNode) -> ASTNode:
        """
        Apply transformation to AST.
        
        Args:
            ast (ASTNode): AST to transform
        
        Returns:
            ASTNode: Transformed AST
        
        Examples:
            >>> transformer = MyTransformer()
            >>> transformed_ast = transformer.transform(ast)
        """
    
    def validate_input(self, ast: ASTNode) -> bool:
        """
        Validate input AST before transformation.
        
        Args:
            ast (ASTNode): AST to validate
        
        Returns:
            bool: True if valid
        """
    
    def validate_output(self, ast: ASTNode) -> bool:
        """
        Validate output AST after transformation.
        
        Args:
            ast (ASTNode): AST to validate
        
        Returns:
            bool: True if valid
        """

class TransformerPipeline:
    """
    Pipeline for applying multiple transformers.
    
    Args:
        transformers (List[BaseTransformer]): Transformers to apply
    
    Examples:
        >>> pipeline = TransformerPipeline([
        ...     HeadingTransformer(add_ids=True),
        ...     LinkTransformer(validate=True),
        ... ])
        >>> result = pipeline.transform(ast)
    """
    
    def __init__(self, transformers: List[BaseTransformer] = None):
        """Initialize pipeline with transformers."""
    
    def add(self, transformer: BaseTransformer) -> None:
        """Add transformer to pipeline."""
    
    def transform(self, ast: ASTNode) -> ASTNode:
        """Apply all transformers in sequence."""
```

### Built-in Transformers

```python
class HeadingTransformer(BaseTransformer):
    """
    Transform heading elements.
    
    Args:
        add_ids (bool): Add ID attributes to headings
        downgrade (int): Increase heading levels by this amount
        max_level (int): Maximum heading level (1-6)
        id_prefix (str): Prefix for generated IDs
        normalize_hierarchy (bool): Fix heading level jumps
        id_generator (Callable): Custom ID generation function
    
    Examples:
        >>> transformer = HeadingTransformer(
        ...     add_ids=True,
        ...     downgrade=1,
        ...     id_prefix="section-"
        ... )
        >>> result = transformer.transform(ast)
    """

class LinkTransformer(BaseTransformer):
    """
    Transform link elements.
    
    Args:
        validate_urls (bool): Validate URL accessibility
        resolve_relative (bool): Convert relative to absolute URLs
        base_url (str): Base URL for relative links
        add_external_indicators (bool): Mark external links
        check_anchors (bool): Validate internal anchors
        timeout (float): URL validation timeout
    
    Examples:
        >>> transformer = LinkTransformer(
        ...     validate_urls=True,
        ...     base_url="https://mysite.com",
        ...     timeout=10
        ... )
        >>> result = transformer.transform(ast)
    """

class TOCTransformer(BaseTransformer):
    """
    Generate table of contents.
    
    Args:
        max_level (int): Maximum heading level to include
        min_level (int): Minimum heading level to include
        insert_position (str): Where to insert TOC
        title (str): TOC title
        numbered (bool): Add numbering to TOC items
        collapsible (bool): Make TOC collapsible
    
    Examples:
        >>> transformer = TOCTransformer(
        ...     max_level=3,
        ...     title="Contents",
        ...     numbered=True
        ... )
        >>> result = transformer.transform(ast)
    """
```

## Renderers

### Renderer Base Classes

```python
class BaseRenderer:
    """
    Base class for AST renderers.
    
    Examples:
        >>> class MyRenderer(BaseRenderer):
        ...     def render_heading(self, node):
        ...         return f"<h{node.level}>{self.render_children(node)}</h{node.level}>"
    """
    
    def render(self, ast: ASTNode) -> str:
        """
        Render AST to output format.
        
        Args:
            ast (ASTNode): AST to render
        
        Returns:
            str: Rendered output
        """
    
    def render_children(self, node: ASTNode) -> str:
        """
        Render child nodes.
        
        Args:
            node (ASTNode): Parent node
        
        Returns:
            str: Rendered children
        """
    
    def add_renderer(self, node_type: str, renderer_func: Callable) -> None:
        """
        Add custom renderer for node type.
        
        Args:
            node_type (str): Node type to handle
            renderer_func (Callable): Rendering function
        
        Examples:
            >>> def render_custom(node):
            ...     return f"<custom>{node.content}</custom>"
            >>> renderer.add_renderer("custom", render_custom)
        """

class MarkdownRenderer(BaseRenderer):
    """
    Render AST to Markdown.
    
    Args:
        preserve_whitespace (bool): Preserve original whitespace
        line_length (int): Maximum line length for wrapping
        indent_size (int): Indentation size for nested elements
    
    Examples:
        >>> renderer = MarkdownRenderer(preserve_whitespace=True)
        >>> markdown = renderer.render(ast)
    """

class HTMLRenderer(BaseRenderer):
    """
    Render AST to HTML.
    
    Args:
        sanitize (bool): Sanitize HTML output
        pretty_print (bool): Format HTML with indentation
        include_meta (bool): Include metadata in HTML
        css_classes (Dict[str, str]): CSS classes for elements
    
    Examples:
        >>> renderer = HTMLRenderer(
        ...     pretty_print=True,
        ...     css_classes={'heading': 'title'}
        ... )
        >>> html = renderer.render(ast)
    """

class JSONRenderer(BaseRenderer):
    """
    Render AST to JSON.
    
    Args:
        pretty (bool): Pretty-print JSON
        indent (int): Indentation level
        include_meta (bool): Include metadata
        compact (bool): Compact representation
    
    Examples:
        >>> renderer = JSONRenderer(pretty=True, indent=2)
        >>> json_str = renderer.render(ast)
    """
```

## Utilities

### Text Processing

```python
def slugify(text: str, 
           separator: str = "-",
           lowercase: bool = True,
           remove_special: bool = True) -> str:
    """
    Convert text to URL-friendly slug.
    
    Args:
        text (str): Text to slugify
        separator (str): Word separator
        lowercase (bool): Convert to lowercase
        remove_special (bool): Remove special characters
    
    Returns:
        str: Slugified text
    
    Examples:
        >>> slug = slugify("Hello World!")
        >>> print(slug)  # "hello-world"
    """

def extract_text(node: ASTNode) -> str:
    """
    Extract all text content from node tree.
    
    Args:
        node (ASTNode): Node to extract text from
    
    Returns:
        str: Extracted text
    
    Examples:
        >>> text = extract_text(paragraph_node)
        >>> print(text)  # "This is some text."
    """

def count_words(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text (str): Text to count
    
    Returns:
        int: Word count
    
    Examples:
        >>> count = count_words("Hello world!")
        >>> print(count)  # 2
    """

def estimate_reading_time(text: str, wpm: int = 200) -> int:
    """
    Estimate reading time in minutes.
    
    Args:
        text (str): Text to analyze
        wpm (int): Words per minute reading speed
    
    Returns:
        int: Estimated reading time in minutes
    
    Examples:
        >>> time_min = estimate_reading_time(article_text)
        >>> print(f"Reading time: {time_min} minutes")
    """
```

### Validation

```python
class ValidationError(Exception):
    """Exception raised for validation errors."""

def validate_ast(ast: ASTNode) -> List[str]:
    """
    Validate AST structure.
    
    Args:
        ast (ASTNode): AST to validate
    
    Returns:
        List[str]: List of validation issues
    
    Examples:
        >>> issues = validate_ast(ast)
        >>> if issues:
        ...     print("Validation issues found:", issues)
    """

def validate_links(ast: ASTNode, 
                  timeout: float = 10,
                  check_anchors: bool = True) -> Dict[str, str]:
    """
    Validate all links in AST.
    
    Args:
        ast (ASTNode): AST containing links
        timeout (float): Request timeout
        check_anchors (bool): Check internal anchors
    
    Returns:
        Dict[str, str]: Link URL to status mapping
    
    Examples:
        >>> results = validate_links(ast)
        >>> broken_links = [url for url, status in results.items() 
        ...                if status != "ok"]
    """

def validate_heading_hierarchy(ast: ASTNode) -> List[str]:
    """
    Validate heading level hierarchy.
    
    Args:
        ast (ASTNode): AST to check
    
    Returns:
        List[str]: List of hierarchy issues
    
    Examples:
        >>> issues = validate_heading_hierarchy(ast)
        >>> for issue in issues:
        ...     print(f"Heading issue: {issue}")
    """
```

## Error Handling

### Exception Classes

```python
class MarkTripyError(Exception):
    """Base exception for marktripy errors."""

class ParseError(MarkTripyError):
    """
    Exception raised when parsing fails.
    
    Attributes:
        message (str): Error message
        line (int): Line number where error occurred
        column (int): Column number where error occurred
        source (str): Source text that caused error
    
    Examples:
        >>> try:
        ...     ast = parse_markdown(malformed_text)
        ... except ParseError as e:
        ...     print(f"Parse error at line {e.line}: {e.message}")
    """

class TransformationError(MarkTripyError):
    """
    Exception raised when AST transformation fails.
    
    Attributes:
        transformer (str): Name of transformer that failed
        node_type (str): Type of node being processed
        details (str): Error details
    
    Examples:
        >>> try:
        ...     result = transformer.transform(ast)
        ... except TransformationError as e:
        ...     print(f"Transformer {e.transformer} failed on {e.node_type}")
    """

class RenderingError(MarkTripyError):
    """
    Exception raised when rendering fails.
    
    Attributes:
        renderer (str): Name of renderer that failed
        node (ASTNode): Node that caused the error
        details (str): Error details
    
    Examples:
        >>> try:
        ...     html = renderer.render(ast)
        ... except RenderingError as e:
        ...     print(f"Rendering failed: {e.details}")
    """

class ValidationError(MarkTripyError):
    """
    Exception raised when validation fails.
    
    Attributes:
        issues (List[str]): List of validation issues
        severity (str): Severity level ('warning', 'error')
    
    Examples:
        >>> try:
        ...     validate_ast(ast)
        ... except ValidationError as e:
        ...     for issue in e.issues:
        ...         print(f"Validation issue: {issue}")
    """
```

## Configuration

### Settings and Options

```python
class Config:
    """
    Global configuration for marktripy.
    
    Attributes:
        default_parser (str): Default parser backend
        default_extensions (List[str]): Default extensions
        cache_enabled (bool): Enable result caching
        max_cache_size (int): Maximum cache entries
        validation_timeout (float): Default validation timeout
    
    Examples:
        >>> from marktripy import config
        >>> config.default_parser = "mistletoe"
        >>> config.default_extensions = ["gfm", "kbd"]
    """
    
    default_parser: str = "markdown-it-py"
    default_extensions: List[str] = []
    cache_enabled: bool = True
    max_cache_size: int = 128
    validation_timeout: float = 10.0
    
    def load_from_file(self, config_path: str) -> None:
        """Load configuration from file."""
    
    def save_to_file(self, config_path: str) -> None:
        """Save configuration to file."""
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""

# Global configuration instance
config = Config()
```

### Environment Variables

```python
# Environment variables that affect marktripy behavior

MARKTRIPY_PARSER = "mistletoe"           # Default parser
MARKTRIPY_EXTENSIONS = "gfm,kbd,math"    # Default extensions
MARKTRIPY_CACHE_DIR = "~/.marktripy"     # Cache directory
MARKTRIPY_CONFIG_FILE = "~/.marktripy/config.yaml"  # Config file
MARKTRIPY_LOG_LEVEL = "INFO"             # Logging level
MARKTRIPY_TIMEOUT = "30"                 # Default timeout
```

## Performance

### Caching

```python
class Cache:
    """
    Result caching for improved performance.
    
    Examples:
        >>> from marktripy.cache import cache
        >>> cache.clear()  # Clear all cached results
        >>> stats = cache.get_stats()  # Get cache statistics
    """
    
    def get(self, key: str) -> Any:
        """Get cached result."""
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Store result in cache."""
    
    def clear(self) -> None:
        """Clear all cached results."""
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""

# Global cache instance
cache = Cache()
```

### Profiling

```python
class Profiler:
    """
    Performance profiling utilities.
    
    Examples:
        >>> from marktripy.profiler import profiler
        >>> with profiler.time("parsing"):
        ...     ast = parse_markdown(text)
        >>> stats = profiler.get_stats()
    """
    
    def time(self, operation: str):
        """Context manager for timing operations."""
    
    def get_stats(self) -> Dict[str, float]:
        """Get performance statistics."""
    
    def reset(self) -> None:
        """Reset all statistics."""

# Global profiler instance
profiler = Profiler()
```

## Type Hints

### Common Types

```python
from typing import Union, List, Dict, Any, Optional, Callable, Iterator

# Type aliases for better readability
NodeType = str
AttributeDict = Dict[str, Any]
ExtensionList = List[Union[str, BaseExtension]]
TransformerList = List[BaseTransformer]
OptionDict = Dict[str, Any]

# Function type hints
ParserFunction = Callable[[str], ASTNode]
RendererFunction = Callable[[ASTNode], str]
TransformerFunction = Callable[[ASTNode], ASTNode]
ValidatorFunction = Callable[[ASTNode], List[str]]
```

This comprehensive API reference provides detailed information about all marktripy classes, functions, and utilities. Use it alongside the other documentation sections for complete understanding of the library's capabilities.