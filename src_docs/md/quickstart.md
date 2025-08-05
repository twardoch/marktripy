# Quick Start Guide

Get up and running with marktripy in minutes! This guide covers the most common use cases with practical examples.

## Basic Usage

### Parse and Render Markdown

```python
from marktripy import parse_markdown, render_markdown

# Simple parsing
markdown_text = """
# Hello World

This is a **bold** statement and this is *italic*.

- Item 1
- Item 2
- Item 3
"""

# Parse to AST
ast = parse_markdown(markdown_text)

# Render back to markdown
result = render_markdown(ast)
print(result)
```

### Convert Markdown to HTML

```python
from marktripy import markdown_to_html

html = markdown_to_html("""
# My Document

Here's some **bold text** and a [link](https://example.com).

```python
print("Hello, World!")
```

> This is a blockquote.
""")

print(html)
```

## AST Exploration

### Understanding the AST Structure

```python
from marktripy import parse_markdown

ast = parse_markdown("# Title\n\nSome **bold** text.")

# Walk through all nodes
for node in ast.walk():
    print(f"Node type: {node.type}")
    if hasattr(node, 'content') and node.content:
        print(f"Content: {node.content}")
    print("---")
```

### Inspecting Node Properties

```python
from marktripy import parse_markdown

ast = parse_markdown("""
# Main Title {#main}

## Subtitle

Some text with **bold** and *italic* formatting.

[Click here](https://example.com "Link title")
""")

def inspect_node(node, depth=0):
    indent = "  " * depth
    print(f"{indent}{node.type}")
    
    # Show attributes if any
    if hasattr(node, 'attrs') and node.attrs:
        print(f"{indent}  attrs: {node.attrs}")
    
    # Show content for text nodes
    if hasattr(node, 'content') and node.content:
        print(f"{indent}  content: {repr(node.content)}")
    
    # Recursively inspect children
    if hasattr(node, 'children'):
        for child in node.children:
            inspect_node(child, depth + 1)

inspect_node(ast)
```

## Basic Transformations

### Downgrade All Headings

```python
from marktripy import parse_markdown, render_markdown

markdown = """
# Chapter 1
## Section 1.1
### Subsection 1.1.1
## Section 1.2
"""

ast = parse_markdown(markdown)

# Downgrade all headings by one level
for node in ast.walk():
    if node.type == "heading" and node.level < 6:
        node.level += 1

result = render_markdown(ast)
print(result)
# Output:
# ## Chapter 1
# ### Section 1.1
# #### Subsection 1.1.1
# ### Section 1.2
```

### Add IDs to Headings

```python
from marktripy import parse_markdown, render_markdown
import re

def slugify(text):
    """Convert text to URL-friendly slug"""
    return re.sub(r'[^\w\s-]', '', text).strip().lower().replace(' ', '-')

markdown = """
# Getting Started
## Installation Guide
## Quick Examples
# Advanced Usage
"""

ast = parse_markdown(markdown)

# Add IDs to all headings
for node in ast.walk():
    if node.type == "heading":
        heading_text = ""
        # Extract text content from heading
        for child in node.children:
            if hasattr(child, 'content'):
                heading_text += child.content
        
        # Create and set ID
        heading_id = slugify(heading_text)
        if not hasattr(node, 'attrs'):
            node.attrs = {}
        node.attrs['id'] = heading_id

result = render_markdown(ast)
print(result)
```

### Extract All Links

```python
from marktripy import parse_markdown

markdown = """
Check out [Python](https://python.org) and [GitHub](https://github.com).

Also see: [Local link](./other-page.md)
"""

ast = parse_markdown(markdown)

links = []
for node in ast.walk():
    if node.type == "link":
        url = node.attrs.get('href', '')
        title = ""
        # Extract link text
        for child in node.children:
            if hasattr(child, 'content'):
                title += child.content
        links.append({'text': title, 'url': url})

for link in links:
    print(f"'{link['text']}' -> {link['url']}")
```

## Working with Extensions

### GitHub Flavored Markdown

```python
from marktripy import Parser

# Create parser with GFM extensions
parser = Parser(extensions=['gfm'])

markdown = """
# Task List

- [x] Completed task
- [ ] Pending task
- [x] Another completed task

## Table

| Name | Age | City |
|------|-----|------|
| Alice | 30 | NYC |
| Bob | 25 | LA |

~~Strikethrough text~~
"""

ast = parser.parse(markdown)
html = parser.render_html(ast)
print(html)
```

### Custom Keyboard Extension

```python
from marktripy import Parser

# Create parser with keyboard extension
parser = Parser(extensions=['kbd'])

markdown = """
To copy text, press ++Ctrl+C++.
To paste, use ++Ctrl+V++.
Press ++Alt+F4++ to close the window.
"""

ast = parser.parse(markdown)
html = parser.render_html(ast)
print(html)
# Output includes: <kbd>Ctrl+C</kbd>, etc.
```

## Document Analysis

### Count Document Elements

```python
from marktripy import parse_markdown
from collections import Counter

markdown = """
# Document Title

## Introduction
Some text here.

## Features
- Feature 1
- Feature 2

### Details
More text with **bold** and *italic*.

## Conclusion
Final thoughts.
"""

ast = parse_markdown(markdown)

# Count node types
node_counts = Counter()
for node in ast.walk():
    node_counts[node.type] += 1

print("Document structure:")
for node_type, count in node_counts.most_common():
    print(f"  {node_type}: {count}")
```

### Extract Table of Contents

```python
from marktripy import parse_markdown

def extract_toc(markdown_text):
    ast = parse_markdown(markdown_text)
    toc = []
    
    for node in ast.walk():
        if node.type == "heading":
            # Extract heading text
            text = ""
            for child in node.children:
                if hasattr(child, 'content'):
                    text += child.content
            
            toc.append({
                'level': node.level,
                'text': text,
                'id': text.lower().replace(' ', '-')
            })
    
    return toc

markdown = """
# User Guide
## Getting Started
### Installation
### Quick Start
## Advanced Features
### Extensions
### Transformers
## API Reference
"""

toc = extract_toc(markdown)
for item in toc:
    indent = "  " * (item['level'] - 1)
    print(f"{indent}- [{item['text']}](#{item['id']})")
```

## File Processing

### Process Single File

```python
from marktripy import parse_markdown, render_markdown
from pathlib import Path

def process_file(input_path, output_path, transform_func=None):
    """Process a markdown file with optional transformation"""
    
    # Read input file
    content = Path(input_path).read_text(encoding='utf-8')
    
    # Parse to AST
    ast = parse_markdown(content)
    
    # Apply transformation if provided
    if transform_func:
        ast = transform_func(ast)
    
    # Render and save
    result = render_markdown(ast)
    Path(output_path).write_text(result, encoding='utf-8')
    
    print(f"Processed {input_path} -> {output_path}")

# Example transformation: add heading IDs
def add_heading_ids(ast):
    for node in ast.walk():
        if node.type == "heading":
            text = "".join(child.content for child in node.children 
                          if hasattr(child, 'content'))
            heading_id = text.lower().replace(' ', '-')
            if not hasattr(node, 'attrs'):
                node.attrs = {}
            node.attrs['id'] = heading_id
    return ast

# Process file
process_file('input.md', 'output.md', add_heading_ids)
```

### Batch Processing

```python
from marktripy import parse_markdown, render_markdown
from pathlib import Path

def batch_process_directory(input_dir, output_dir, pattern="*.md"):
    """Process all markdown files in a directory"""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for md_file in input_path.glob(pattern):
        print(f"Processing {md_file.name}...")
        
        # Read and parse
        content = md_file.read_text(encoding='utf-8')
        ast = parse_markdown(content)
        
        # Transform: downgrade headings
        for node in ast.walk():
            if node.type == "heading" and node.level < 6:
                node.level += 1
        
        # Save result
        result = render_markdown(ast)
        output_file = output_path / md_file.name
        output_file.write_text(result, encoding='utf-8')
    
    print("Batch processing complete!")

# Process all markdown files
batch_process_directory('docs/', 'processed_docs/')
```

## Error Handling

### Robust Parsing

```python
from marktripy import parse_markdown
import logging

def safe_parse(markdown_text):
    """Parse markdown with error handling"""
    try:
        ast = parse_markdown(markdown_text)
        return ast, None
    except Exception as e:
        logging.error(f"Failed to parse markdown: {e}")
        return None, str(e)

# Example usage
markdown = "# Valid heading\n\nSome text..."
ast, error = safe_parse(markdown)

if ast:
    print("Parsing successful!")
    # Process the AST
else:
    print(f"Parsing failed: {error}")
```

### Validation

```python
from marktripy import parse_markdown

def validate_document(markdown_text):
    """Validate document structure"""
    issues = []
    
    try:
        ast = parse_markdown(markdown_text)
    except Exception as e:
        return [f"Parse error: {e}"]
    
    # Check for heading hierarchy
    heading_levels = []
    for node in ast.walk():
        if node.type == "heading":
            heading_levels.append(node.level)
    
    # Validate heading sequence
    for i, level in enumerate(heading_levels[1:], 1):
        prev_level = heading_levels[i-1]
        if level > prev_level + 1:
            issues.append(f"Heading level jump: H{prev_level} to H{level}")
    
    # Check for empty links
    for node in ast.walk():
        if node.type == "link":
            href = node.attrs.get('href', '')
            if not href:
                issues.append("Empty link found")
    
    return issues

# Validate document
markdown = """
# Title
### Subsection  # This should be H2
"""

issues = validate_document(markdown)
if issues:
    print("Document issues found:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("Document is valid!")
```

## Next Steps

Now that you've seen the basics:

1. **Learn about [Core Concepts](core-concepts.md)** to understand marktripy's architecture
2. **Explore [AST Manipulation](ast-manipulation.md)** for advanced document editing
3. **Try the [Extensions System](extensions.md)** to add custom syntax
4. **Use [Transformers](transformers.md)** for common document processing tasks
5. **Check out [CLI Usage](cli.md)** for command-line tools

## Common Patterns

### Document Template Processing

```python
from marktripy import parse_markdown, render_markdown
import datetime

def process_template(template_markdown, variables):
    """Process a markdown template with variables"""
    ast = parse_markdown(template_markdown)
    
    # Replace template variables
    for node in ast.walk():
        if hasattr(node, 'content') and node.content:
            for key, value in variables.items():
                node.content = node.content.replace(f"{{{key}}}", str(value))
    
    return render_markdown(ast)

template = """
# Report for {date}

## Summary
Total items processed: {count}
Status: {status}
"""

variables = {
    'date': datetime.date.today().strftime('%Y-%m-%d'),
    'count': 42,
    'status': 'Complete'
}

result = process_template(template, variables)
print(result)
```

This quick start guide covers the essential patterns you'll use with marktripy. For more advanced features, continue to the detailed guides!