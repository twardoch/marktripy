# Transformers

Transformers are pre-built utilities for common document processing tasks. Learn how to use built-in transformers and create your own for systematic document manipulation.

## Transformer Architecture

### Base Transformer Class

```python
from marktripy.transformers import BaseTransformer

class CustomTransformer(BaseTransformer):
    """Base class for all transformers"""
    
    def __init__(self, **options):
        self.options = options
    
    def transform(self, ast):
        """Main transformation method - must be implemented"""
        raise NotImplementedError
    
    def validate_input(self, ast):
        """Validate input AST before transformation"""
        return True
    
    def validate_output(self, ast):
        """Validate output AST after transformation"""
        return True
```

### Transformer Pipeline

```python
from marktripy import parse_markdown, render_markdown
from marktripy.transformers import TransformerPipeline

# Create pipeline of transformers
pipeline = TransformerPipeline([
    HeadingTransformer(add_ids=True, downgrade=1),
    LinkTransformer(validate=True, add_external_indicators=True),
    TOCTransformer(max_level=3),
])

# Apply pipeline to document
markdown = "# Title\n\nSome content..."
ast = parse_markdown(markdown)
transformed_ast = pipeline.transform(ast)
result = render_markdown(transformed_ast)
```

## Built-in Transformers

### HeadingTransformer

Manipulate heading structure and add metadata:

```python
from marktripy.transformers import HeadingTransformer

# Basic heading manipulation
transformer = HeadingTransformer(
    add_ids=True,           # Add ID attributes
    downgrade=1,            # Increase all heading levels by 1
    max_level=6,            # Cap maximum heading level
    id_prefix="section-",   # Prefix for generated IDs
    normalize_hierarchy=True # Fix heading level jumps
)

markdown = """
# Main Title
### Subsection (level jump)
## Proper Section
"""

ast = parse_markdown(markdown)
ast = transformer.transform(ast)
result = render_markdown(ast)

# Result:
# ## Main Title {#section-main-title}
# ### Subsection {#section-subsection}
# ### Proper Section {#section-proper-section}
```

### Advanced Heading Operations

```python
from marktripy.transformers import HeadingTransformer

# Custom ID generation
def custom_id_generator(heading_text):
    """Generate custom IDs based on content"""
    return f"h-{hash(heading_text) % 10000}"

transformer = HeadingTransformer(
    id_generator=custom_id_generator,
    add_anchor_links=True,      # Add clickable anchor links
    wrap_in_sections=True,      # Wrap content in section tags
)

# Extract heading information
class HeadingAnalyzer(HeadingTransformer):
    def __init__(self):
        super().__init__()
        self.headings = []
    
    def transform(self, ast):
        for node in ast.walk():
            if node.type == "heading":
                self.headings.append({
                    'level': node.level,
                    'text': self.extract_text(node),
                    'id': node.attrs.get('id'),
                })
        return ast

analyzer = HeadingAnalyzer()
ast = analyzer.transform(ast)
print("Document headings:", analyzer.headings)
```

### LinkTransformer

Process and validate links throughout the document:

```python
from marktripy.transformers import LinkTransformer

# Comprehensive link processing
transformer = LinkTransformer(
    validate_urls=True,         # Check if URLs are accessible
    resolve_relative=True,      # Convert relative to absolute URLs
    base_url="https://mysite.com",
    add_external_indicators=True, # Mark external links
    check_anchors=True,         # Validate internal anchors
    timeout=5,                  # URL validation timeout
)

markdown = """
Check out [Python](https://python.org) and [local page](./docs.md).
Also see [internal link](#section1) and [broken link](http://nonexistent.com).
"""

ast = parse_markdown(markdown)
result = transformer.transform(ast)

# Access validation results
if hasattr(transformer, 'validation_results'):
    for link, status in transformer.validation_results.items():
        print(f"{link}: {status}")
```

### Link Manipulation Examples

```python
from marktripy.transformers import LinkTransformer

# Custom link processing
class LinkProcessor(LinkTransformer):
    def __init__(self, **options):
        super().__init__(**options)
        self.processed_links = []
    
    def process_link(self, link_node):
        """Custom link processing logic"""
        href = link_node.attrs.get('href', '')
        
        # Log all processed links
        self.processed_links.append(href)
        
        # Add tracking parameters to external links
        if self.is_external_url(href):
            separator = '&' if '?' in href else '?'
            link_node.attrs['href'] = f"{href}{separator}utm_source=mydocs"
        
        # Add title attributes for better accessibility
        if 'title' not in link_node.attrs:
            text = self.extract_text(link_node)
            link_node.attrs['title'] = f"Link to {text}"
        
        return link_node

# Convert relative links to absolute
class RelativeLinkConverter(LinkTransformer):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url.rstrip('/')
    
    def process_link(self, link_node):
        href = link_node.attrs.get('href', '')
        
        # Convert relative URLs
        if href.startswith('./') or href.startswith('../'):
            link_node.attrs['href'] = f"{self.base_url}/{href.lstrip('./')}"
        elif href.startswith('/'):
            link_node.attrs['href'] = f"{self.base_url}{href}"
        
        return link_node
```

### TOCTransformer

Generate table of contents from document headings:

```python
from marktripy.transformers import TOCTransformer

# Basic TOC generation
transformer = TOCTransformer(
    max_level=3,               # Include headings up to H3
    min_level=1,               # Start from H1
    insert_position="after_title", # Where to insert TOC
    title="Table of Contents", # TOC title
    numbered=True,             # Add numbering to TOC items
    collapsible=True,          # Make TOC collapsible
)

markdown = """
# User Guide

## Getting Started
### Installation
### Configuration

## Advanced Usage
### Custom Extensions
### Performance Tuning

## API Reference
### Core Classes
### Utility Functions
"""

ast = parse_markdown(markdown)
ast = transformer.transform(ast)
result = render_markdown(ast)
```

### Advanced TOC Features

```python
from marktripy.transformers import TOCTransformer

# Custom TOC formatting
class CustomTOCTransformer(TOCTransformer):
    def __init__(self, **options):
        super().__init__(**options)
        self.toc_items = []
    
    def generate_toc_item(self, heading_node, level, number=None):
        """Custom TOC item generation"""
        text = self.extract_text(heading_node)
        anchor = heading_node.attrs.get('id', self.generate_anchor(text))
        
        # Custom formatting based on level
        if level == 1:
            icon = "📚"
        elif level == 2:
            icon = "📖"
        else:
            icon = "📄"
        
        item_text = f"{icon} {text}"
        if number:
            item_text = f"{number}. {item_text}"
        
        return {
            'text': item_text,
            'anchor': anchor,
            'level': level
        }
    
    def format_toc(self, toc_items):
        """Custom TOC formatting"""
        lines = ["## 📋 Contents\n"]
        
        for item in toc_items:
            indent = "  " * (item['level'] - 1)
            lines.append(f"{indent}- [{item['text']}](#{item['anchor']})")
        
        return "\n".join(lines) + "\n"

# Extract TOC data without inserting
class TOCExtractor(TOCTransformer):
    def __init__(self):
        super().__init__(insert_toc=False)
        self.toc_data = []
    
    def transform(self, ast):
        """Extract TOC data for external use"""
        for node in ast.walk():
            if node.type == "heading":
                self.toc_data.append({
                    'level': node.level,
                    'text': self.extract_text(node),
                    'id': node.attrs.get('id'),
                    'line_number': getattr(node, 'line_number', None)
                })
        return ast
```

### IdGeneratorTransformer

Add unique IDs to various elements:

```python
from marktripy.transformers import IdGeneratorTransformer

# Generate IDs for multiple element types
transformer = IdGeneratorTransformer(
    elements=['heading', 'table', 'code_block', 'image'],
    prefix_map={
        'heading': 'h-',
        'table': 'table-',
        'code_block': 'code-',
        'image': 'img-'
    },
    counter_start=1,
    unique_check=True,         # Ensure all IDs are unique
    preserve_existing=True,    # Don't overwrite existing IDs
)

markdown = """
# First Heading

| Column 1 | Column 2 |
|----------|----------|
| A        | B        |

```python
print("Hello")
```

![Sample Image](image.png)

# Second Heading
"""

ast = parse_markdown(markdown)
ast = transformer.transform(ast)
```

### Custom ID Generation

```python
from marktripy.transformers import IdGeneratorTransformer
import hashlib

class SmartIdGenerator(IdGeneratorTransformer):
    def __init__(self):
        super().__init__()
        self.used_ids = set()
        self.content_hashes = {}
    
    def generate_id(self, node, element_type):
        """Generate smart IDs based on content"""
        
        if element_type == "heading":
            text = self.extract_text(node)
            # Use slugified text for headings
            base_id = self.slugify(text)
        
        elif element_type == "code_block":
            # Use language and content hash for code blocks
            lang = node.attrs.get('lang', 'code')
            content = getattr(node, 'content', '')
            content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
            base_id = f"{lang}-{content_hash}"
        
        elif element_type == "table":
            # Use column count and first cell content
            first_cell = self.get_first_table_cell(node)
            if first_cell:
                text = self.extract_text(first_cell)[:20]
                base_id = f"table-{self.slugify(text)}"
            else:
                base_id = "table-unknown"
        
        else:
            # Generic ID generation
            base_id = f"{element_type}-{len(self.used_ids) + 1}"
        
        # Ensure uniqueness
        final_id = base_id
        counter = 1
        while final_id in self.used_ids:
            final_id = f"{base_id}-{counter}"
            counter += 1
        
        self.used_ids.add(final_id)
        return final_id
```

## Content Transformation

### TextTransformer

Process text content throughout the document:

```python
from marktripy.transformers import TextTransformer

# Basic text transformations
transformer = TextTransformer(
    normalize_whitespace=True,  # Clean up extra spaces
    fix_typography=True,        # Smart quotes, dashes
    auto_correct=True,          # Basic spelling corrections
    preserve_code=True,         # Don't modify code content
)

# Custom text processing
class TextProcessor(TextTransformer):
    def __init__(self, replacements=None):
        super().__init__()
        self.replacements = replacements or {}
    
    def process_text(self, text_node):
        """Custom text processing"""
        content = text_node.content
        
        # Apply replacements
        for old, new in self.replacements.items():
            content = content.replace(old, new)
        
        # Normalize whitespace
        content = ' '.join(content.split())
        
        # Smart typography
        content = content.replace('--', '—')  # Em dash
        content = content.replace("'", "'")   # Smart apostrophe
        
        text_node.content = content
        return text_node

# Example usage
replacements = {
    'Javascript': 'JavaScript',
    'Github': 'GitHub',
    'API': 'API',
}

processor = TextProcessor(replacements)
ast = processor.transform(ast)
```

### LinkReferenceTransformer

Convert inline links to reference-style links:

```python
from marktripy.transformers import LinkReferenceTransformer

# Convert to reference links
transformer = LinkReferenceTransformer(
    min_url_length=30,         # Only convert long URLs
    alphabetical_refs=True,    # Sort references alphabetically
    append_references=True,    # Add reference section at end
    reference_style="numbered", # "numbered" or "named"
)

markdown = """
Check out [Python documentation](https://docs.python.org/3/library/index.html) 
and [GitHub repository](https://github.com/python/cpython) for more information.

Also see [Python.org](https://python.org) for general info.
"""

ast = parse_markdown(markdown)
ast = transformer.transform(ast)
result = render_markdown(ast)

# Result:
# Check out [Python documentation][1] and [GitHub repository][2] for more information.
# Also see [Python.org](https://python.org) for general info.
#
# [1]: https://docs.python.org/3/library/index.html
# [2]: https://github.com/python/cpython
```

## Document Structure Transformers

### SectionTransformer

Reorganize document sections:

```python
from marktripy.transformers import SectionTransformer

# Reorder sections based on headings
transformer = SectionTransformer(
    section_order=['Introduction', 'Installation', 'Usage', 'API Reference'],
    auto_number_sections=True,
    add_section_breaks=True,
    create_section_nav=True,
)

# Custom section reorganization
class DocumentStructurer(SectionTransformer):
    def __init__(self):
        super().__init__()
        self.sections = []
    
    def extract_sections(self, ast):
        """Extract sections based on H1 headings"""
        current_section = None
        
        for node in ast.walk():
            if node.type == "heading" and node.level == 1:
                if current_section:
                    self.sections.append(current_section)
                
                current_section = {
                    'title': self.extract_text(node),
                    'heading_node': node,
                    'content': []
                }
            elif current_section:
                current_section['content'].append(node)
        
        if current_section:
            self.sections.append(current_section)
    
    def reorder_sections(self, order):
        """Reorder sections according to specified order"""
        section_map = {s['title']: s for s in self.sections}
        self.sections = [section_map[title] for title in order if title in section_map]
```

### FilterTransformer

Remove or modify content based on criteria:

```python
from marktripy.transformers import FilterTransformer

# Content filtering
transformer = FilterTransformer(
    remove_comments=True,      # Remove HTML comments
    remove_empty_paragraphs=True,
    filter_by_class=["draft", "internal"],  # Remove elements with these classes
    max_heading_level=4,       # Remove deep headings
)

# Custom filtering
class ContentFilter(FilterTransformer):
    def __init__(self, allowed_elements=None, blocked_words=None):
        super().__init__()
        self.allowed_elements = allowed_elements or []
        self.blocked_words = blocked_words or []
    
    def should_keep_node(self, node):
        """Determine if node should be kept"""
        
        # Filter by element type
        if self.allowed_elements and node.type not in self.allowed_elements:
            return False
        
        # Filter by content
        if node.type == "text" and node.content:
            for blocked_word in self.blocked_words:
                if blocked_word.lower() in node.content.lower():
                    return False
        
        return True
    
    def transform(self, ast):
        """Apply filtering to AST"""
        self.filter_children(ast)
        return ast
    
    def filter_children(self, node):
        """Recursively filter child nodes"""
        if hasattr(node, 'children'):
            node.children = [
                child for child in node.children 
                if self.should_keep_node(child)
            ]
            
            for child in node.children:
                self.filter_children(child)

# Usage
content_filter = ContentFilter(
    allowed_elements=['heading', 'paragraph', 'text', 'strong', 'emphasis'],
    blocked_words=['TODO', 'FIXME', 'DRAFT']
)
```

## Validation Transformers

### ValidatorTransformer

Validate document structure and content:

```python
from marktripy.transformers import ValidatorTransformer

# Comprehensive validation
validator = ValidatorTransformer(
    check_heading_hierarchy=True,
    check_link_validity=True,
    check_image_accessibility=True,
    check_table_structure=True,
    report_warnings=True,
)

# Custom validation
class DocumentValidator(ValidatorTransformer):
    def __init__(self):
        super().__init__()
        self.issues = []
    
    def validate_heading_hierarchy(self, ast):
        """Check for proper heading hierarchy"""
        heading_levels = []
        
        for node in ast.walk():
            if node.type == "heading":
                heading_levels.append(node.level)
        
        # Check for level jumps
        for i, level in enumerate(heading_levels[1:], 1):
            prev_level = heading_levels[i-1]
            if level > prev_level + 1:
                self.issues.append(
                    f"Heading level jump: H{prev_level} to H{level}"
                )
    
    def validate_links(self, ast):
        """Validate link structure"""
        for node in ast.walk():
            if node.type == "link":
                href = node.attrs.get('href', '')
                
                if not href:
                    self.issues.append("Empty link found")
                
                if href.startswith('#'):
                    # Check if anchor exists
                    anchor = href[1:]
                    if not self.anchor_exists(ast, anchor):
                        self.issues.append(f"Broken anchor: {href}")
    
    def anchor_exists(self, ast, anchor_id):
        """Check if anchor ID exists in document"""
        for node in ast.walk():
            if hasattr(node, 'attrs') and node.attrs.get('id') == anchor_id:
                return True
        return False
    
    def transform(self, ast):
        """Run all validations"""
        self.issues = []
        self.validate_heading_hierarchy(ast)
        self.validate_links(ast)
        return ast

# Usage
validator = DocumentValidator()
ast = validator.transform(ast)

if validator.issues:
    print("Document issues found:")
    for issue in validator.issues:
        print(f"  - {issue}")
```

## Custom Transformers

### Creating Domain-Specific Transformers

```python
from marktripy.transformers import BaseTransformer

class APIDocTransformer(BaseTransformer):
    """Transformer for API documentation"""
    
    def __init__(self, api_base_url=None, add_try_links=True):
        self.api_base_url = api_base_url
        self.add_try_links = add_try_links
        self.endpoints = []
    
    def transform(self, ast):
        """Transform API documentation"""
        self.process_api_endpoints(ast)
        self.add_code_examples(ast)
        if self.add_try_links:
            self.add_try_it_links(ast)
        return ast
    
    def process_api_endpoints(self, ast):
        """Process API endpoint definitions"""
        for node in ast.walk():
            if (node.type == "code_block" and 
                node.attrs.get('lang') == 'http'):
                
                endpoint = self.parse_http_block(node)
                if endpoint:
                    self.endpoints.append(endpoint)
                    self.enhance_endpoint_block(node, endpoint)
    
    def parse_http_block(self, code_node):
        """Parse HTTP code block for endpoint info"""
        content = getattr(code_node, 'content', '')
        lines = content.split('\n')
        
        if lines:
            first_line = lines[0].strip()
            parts = first_line.split()
            if len(parts) >= 2:
                return {
                    'method': parts[0],
                    'path': parts[1],
                    'full_url': f"{self.api_base_url}{parts[1]}" if self.api_base_url else parts[1]
                }
        return None
    
    def enhance_endpoint_block(self, code_node, endpoint):
        """Add metadata to endpoint code blocks"""
        code_node.attrs.update({
            'endpoint_method': endpoint['method'],
            'endpoint_path': endpoint['path'],
            'api_endpoint': True
        })
    
    def add_try_it_links(self, ast):
        """Add 'Try it' links after API endpoints"""
        # Implementation would add interactive links
        pass

class BlogPostTransformer(BaseTransformer):
    """Transformer for blog posts"""
    
    def __init__(self, add_reading_time=True, add_social_share=True):
        self.add_reading_time = add_reading_time
        self.add_social_share = add_social_share
    
    def transform(self, ast):
        """Transform blog post content"""
        if self.add_reading_time:
            self.add_reading_time_estimate(ast)
        
        if self.add_social_share:
            self.add_social_sharing_buttons(ast)
        
        self.optimize_images(ast)
        return ast
    
    def add_reading_time_estimate(self, ast):
        """Calculate and add reading time"""
        word_count = self.count_words(ast)
        reading_time = max(1, word_count // 200)  # Assume 200 WPM
        
        # Add reading time after title
        reading_time_node = self.create_reading_time_node(reading_time)
        
        # Insert after first heading if it exists
        if ast.children and ast.children[0].type == "heading":
            ast.children.insert(1, reading_time_node)
    
    def count_words(self, ast):
        """Count words in document"""
        word_count = 0
        for node in ast.walk():
            if node.type == "text" and hasattr(node, 'content'):
                words = node.content.split()
                word_count += len([w for w in words if w.strip()])
        return word_count
    
    def create_reading_time_node(self, minutes):
        """Create reading time display node"""
        return {
            'type': 'paragraph',
            'children': [{
                'type': 'text',
                'content': f"📖 Estimated reading time: {minutes} minute{'s' if minutes != 1 else ''}",
                'children': [],
                'attrs': {}
            }],
            'attrs': {'class': 'reading-time'}
        }
```

## Transformer Utilities

### Pipeline Management

```python
from marktripy.transformers import TransformerPipeline

# Create reusable pipelines
standard_pipeline = TransformerPipeline([
    HeadingTransformer(add_ids=True),
    LinkTransformer(validate=True),
    TextTransformer(normalize_whitespace=True),
])

blog_pipeline = TransformerPipeline([
    HeadingTransformer(add_ids=True, max_level=4),
    BlogPostTransformer(add_reading_time=True),
    TOCTransformer(max_level=3),
    ValidatorTransformer(check_heading_hierarchy=True),
])

api_pipeline = TransformerPipeline([
    HeadingTransformer(add_ids=True),
    APIDocTransformer(api_base_url="https://api.example.com"),
    TOCTransformer(title="API Endpoints"),
])

# Pipeline with conditional transformers
conditional_pipeline = TransformerPipeline()
conditional_pipeline.add_if(
    condition=lambda ast: has_code_blocks(ast),
    transformer=CodeEnhancementTransformer()
)
conditional_pipeline.add_if(
    condition=lambda ast: has_tables(ast),
    transformer=TableSortTransformer()
)
```

### Performance Monitoring

```python
import time
from marktripy.transformers import BaseTransformer

class TimedTransformer(BaseTransformer):
    """Wrapper to measure transformer performance"""
    
    def __init__(self, transformer):
        self.transformer = transformer
        self.execution_time = 0
    
    def transform(self, ast):
        start_time = time.time()
        result = self.transformer.transform(ast)
        self.execution_time = time.time() - start_time
        return result

# Benchmark pipeline performance
timed_pipeline = TransformerPipeline([
    TimedTransformer(HeadingTransformer(add_ids=True)),
    TimedTransformer(LinkTransformer(validate=True)),
    TimedTransformer(TOCTransformer()),
])

ast = timed_pipeline.transform(ast)

# Report performance
for i, transformer in enumerate(timed_pipeline.transformers):
    if isinstance(transformer, TimedTransformer):
        print(f"Transformer {i}: {transformer.execution_time:.3f}s")
```

## Best Practices

### Transformer Design Principles

1. **Single Responsibility**: Each transformer should have one clear purpose
2. **Idempotency**: Running the same transformer multiple times should be safe
3. **Validation**: Always validate input and output AST structure
4. **Performance**: Minimize AST traversals by combining operations
5. **Error Handling**: Handle malformed input gracefully

### Common Patterns

```python
# ✅ Good: Single-pass traversal
class EfficientTransformer(BaseTransformer):
    def transform(self, ast):
        for node in ast.walk():
            if node.type == "heading":
                self.process_heading(node)
            elif node.type == "link":
                self.process_link(node)
            elif node.type == "text":
                self.process_text(node)
        return ast

# ❌ Bad: Multiple traversals
class InefficientTransformer(BaseTransformer):
    def transform(self, ast):
        # Three separate traversals
        for node in ast.walk():
            if node.type == "heading":
                self.process_heading(node)
        
        for node in ast.walk():
            if node.type == "link":
                self.process_link(node)
        
        for node in ast.walk():
            if node.type == "text":
                self.process_text(node)
        return ast
```

## Next Steps

Transformers provide powerful document processing capabilities. Continue with:

1. **[Performance](performance.md)** - Optimize transformer performance
2. **[CLI Usage](cli.md)** - Apply transformers from command line
3. **[API Reference](api-reference.md)** - Complete transformer API documentation

With transformers, you can create sophisticated document processing workflows that handle complex transformations while maintaining document integrity and performance.