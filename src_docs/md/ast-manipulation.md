# AST Manipulation

Master the art of programmatically modifying Markdown document structure. This comprehensive guide covers everything from basic node traversal to complex document transformations.

## Understanding AST Traversal

### Basic Node Walking

The foundation of AST manipulation is traversing the document tree:

```python
from marktripy import parse_markdown

markdown = """
# Document Title

## Section 1
Some text with **bold** and *italic* formatting.

## Section 2
- List item 1
- List item 2

> A blockquote with [a link](https://example.com).
"""

ast = parse_markdown(markdown)

# Walk through all nodes
def analyze_document(ast):
    for node in ast.walk():
        print(f"Type: {node.type}")
        if hasattr(node, 'level'):
            print(f"  Level: {node.level}")
        if hasattr(node, 'content') and node.content:
            print(f"  Content: {repr(node.content)}")
        if hasattr(node, 'attrs') and node.attrs:
            print(f"  Attributes: {node.attrs}")
        print()

analyze_document(ast)
```

### Targeted Node Finding

Find specific nodes efficiently:

```python
from marktripy import parse_markdown

ast = parse_markdown(markdown)

# Find all headings
headings = [node for node in ast.walk() if node.type == "heading"]
print(f"Found {len(headings)} headings")

# Find nodes by multiple criteria
important_headings = [
    node for node in ast.walk() 
    if node.type == "heading" and node.level <= 2
]

# Find all links
links = [node for node in ast.walk() if node.type == "link"]
for link in links:
    href = link.attrs.get('href', '')
    text = ''.join(child.content for child in link.children if hasattr(child, 'content'))
    print(f"Link: '{text}' -> {href}")

# Find text nodes containing specific content
search_term = "example"
matching_text = [
    node for node in ast.walk()
    if node.type == "text" and search_term.lower() in node.content.lower()
]
```

### Advanced Traversal Patterns

```python
from marktripy import parse_markdown

def traverse_with_path(node, path=[]):
    """Traverse nodes while tracking the path from root"""
    current_path = path + [node.type]
    
    # Process current node
    print(f"Path: {' -> '.join(current_path)}")
    
    # Recursively traverse children
    if hasattr(node, 'children'):
        for child in node.children:
            traverse_with_path(child, current_path)

def find_parent_relationships(ast):
    """Build a parent-child relationship map"""
    parent_map = {}
    
    def build_map(node, parent=None):
        parent_map[id(node)] = parent
        if hasattr(node, 'children'):
            for child in node.children:
                build_map(child, node)
    
    build_map(ast)
    return parent_map

# Usage
ast = parse_markdown(markdown)
parent_map = find_parent_relationships(ast)

# Find parent of a specific node
for node in ast.walk():
    if node.type == "strong":
        parent = parent_map[id(node)]
        print(f"Bold text found in {parent.type}")
```

## Basic Transformations

### Text Content Modification

```python
from marktripy import parse_markdown, render_markdown

def transform_text(ast, transform_func):
    """Apply a transformation function to all text nodes"""
    for node in ast.walk():
        if node.type == "text" and node.content:
            node.content = transform_func(node.content)
    return ast

# Example transformations
markdown = "This is UPPERCASE text with some lowercase."
ast = parse_markdown(markdown)

# Convert to title case
ast = transform_text(ast, lambda text: text.title())
print(render_markdown(ast))

# Replace specific words
def replace_words(text):
    replacements = {
        'old': 'new',
        'bad': 'good',
        'wrong': 'right'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

ast = transform_text(ast, replace_words)
```

### Heading Manipulation

```python
from marktripy import parse_markdown, render_markdown
import re

def adjust_heading_levels(ast, adjustment):
    """Increase or decrease all heading levels"""
    for node in ast.walk():
        if node.type == "heading":
            new_level = node.level + adjustment
            # Clamp to valid range (1-6)
            node.level = max(1, min(6, new_level))
    return ast

def add_heading_ids(ast):
    """Add ID attributes to all headings"""
    def slugify(text):
        # Convert to lowercase, replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', text).strip().lower()
        return re.sub(r'[-\s]+', '-', slug)
    
    for node in ast.walk():
        if node.type == "heading":
            # Extract text content
            text = ""
            for child in node.children:
                if hasattr(child, 'content'):
                    text += child.content
            
            # Create ID
            heading_id = slugify(text)
            if not hasattr(node, 'attrs'):
                node.attrs = {}
            node.attrs['id'] = heading_id
    
    return ast

def normalize_heading_hierarchy(ast):
    """Ensure proper heading hierarchy (no level jumps)"""
    heading_stack = []
    
    for node in ast.walk():
        if node.type == "heading":
            # Find appropriate level based on hierarchy
            while heading_stack and heading_stack[-1] >= node.level:
                heading_stack.pop()
            
            if heading_stack:
                # Ensure no level jumps
                max_allowed = heading_stack[-1] + 1
                if node.level > max_allowed:
                    node.level = max_allowed
            else:
                # First heading should be level 1
                node.level = 1
            
            heading_stack.append(node.level)
    
    return ast

# Example usage
markdown = """
# Title
### Subsection (should be H2)
##### Deep section (should be H3)
## Proper section
"""

ast = parse_markdown(markdown)
ast = normalize_heading_hierarchy(ast)
ast = add_heading_ids(ast)
result = render_markdown(ast)
print(result)
```

### Link Processing

```python
from marktripy import parse_markdown, render_markdown
from urllib.parse import urljoin, urlparse

def process_links(ast, base_url=None, transform_func=None):
    """Process all links in the document"""
    for node in ast.walk():
        if node.type == "link":
            href = node.attrs.get('href', '')
            
            # Apply base URL for relative links
            if base_url and not urlparse(href).netloc:
                node.attrs['href'] = urljoin(base_url, href)
            
            # Apply custom transformation
            if transform_func:
                node.attrs['href'] = transform_func(href)
    
    return ast

def add_external_link_indicators(ast):
    """Add indicators for external links"""
    for node in ast.walk():
        if node.type == "link":
            href = node.attrs.get('href', '')
            if urlparse(href).netloc:  # External link
                # Add external link indicator
                external_indicator = {
                    'type': 'text',
                    'content': ' ↗',
                    'children': [],
                    'attrs': {}
                }
                node.children.append(external_indicator)
    
    return ast

def validate_links(ast):
    """Find broken or suspicious links"""
    issues = []
    
    for node in ast.walk():
        if node.type == "link":
            href = node.attrs.get('href', '')
            
            if not href:
                issues.append("Empty link found")
            elif href.startswith('javascript:'):
                issues.append("Suspicious JavaScript link found")
            elif href.startswith('#') and len(href) == 1:
                issues.append("Empty anchor link found")
    
    return issues

# Example usage
markdown = """
Check out [Python](https://python.org) and [local page](./local.md).
Also see [empty link]() and [anchor](#section).
"""

ast = parse_markdown(markdown)
ast = process_links(ast, base_url="https://mysite.com/")
ast = add_external_link_indicators(ast)

issues = validate_links(ast)
if issues:
    print("Link issues:", issues)

result = render_markdown(ast)
print(result)
```

## Advanced Transformations

### List Manipulation

```python
from marktripy import parse_markdown, render_markdown

def convert_to_task_list(ast):
    """Convert regular lists to task lists"""
    for node in ast.walk():
        if node.type == "list" and not node.attrs.get('ordered', False):
            # Convert each list item to a task item
            for item in node.children:
                if item.type == "list_item":
                    item.attrs = item.attrs or {}
                    item.attrs['checked'] = False  # Unchecked by default
    return ast

def sort_list_items(ast, sort_key=None):
    """Sort list items alphabetically or by custom key"""
    for node in ast.walk():
        if node.type == "list":
            # Extract text from list items for sorting
            items_with_text = []
            for item in node.children:
                if item.type == "list_item":
                    text = extract_text_content(item)
                    items_with_text.append((text, item))
            
            # Sort by text content or custom key
            if sort_key:
                items_with_text.sort(key=lambda x: sort_key(x[0]))
            else:
                items_with_text.sort(key=lambda x: x[0].lower())
            
            # Update children order
            node.children = [item for text, item in items_with_text]
    
    return ast

def extract_text_content(node):
    """Extract all text content from a node and its children"""
    text = ""
    for child in node.walk():
        if hasattr(child, 'content') and child.content:
            text += child.content
    return text

# Example usage
markdown = """
# Shopping List

- Bananas
- Apples
- Carrots
- Bread
"""

ast = parse_markdown(markdown)
ast = sort_list_items(ast)
ast = convert_to_task_list(ast)
result = render_markdown(ast)
print(result)
```

### Table Manipulation

```python
from marktripy import parse_markdown, render_markdown

def transform_table(ast, transform_func):
    """Apply transformations to table data"""
    for node in ast.walk():
        if node.type == "table":
            # Process table rows
            for row in node.children:
                if row.type == "table_row":
                    for cell in row.children:
                        if cell.type == "table_cell":
                            transform_func(cell)
    return ast

def add_table_styling(ast):
    """Add styling classes to tables"""
    for node in ast.walk():
        if node.type == "table":
            node.attrs = node.attrs or {}
            node.attrs['class'] = 'styled-table'
    return ast

def sort_table_by_column(ast, column_index=0, reverse=False):
    """Sort table rows by a specific column"""
    for node in ast.walk():
        if node.type == "table":
            header_row = None
            data_rows = []
            
            for row in node.children:
                if row.type == "table_row":
                    # Assume first row is header
                    if header_row is None:
                        header_row = row
                    else:
                        data_rows.append(row)
            
            # Sort data rows by specified column
            def get_cell_text(row, col_idx):
                if col_idx < len(row.children):
                    cell = row.children[col_idx]
                    return extract_text_content(cell)
                return ""
            
            data_rows.sort(
                key=lambda row: get_cell_text(row, column_index),
                reverse=reverse
            )
            
            # Reconstruct table
            node.children = [header_row] + data_rows
    
    return ast

# Example usage with GFM table extension
markdown = """
| Name | Age | City |
|------|-----|------|
| Bob | 25 | NYC |
| Alice | 30 | LA |
| Charlie | 20 | Chicago |
"""

# Note: Requires GFM extension for table parsing
from marktripy import Parser
parser = Parser(extensions=['gfm'])
ast = parser.parse(markdown)

ast = sort_table_by_column(ast, column_index=1)  # Sort by age
ast = add_table_styling(ast)
result = parser.render_markdown(ast)
print(result)
```

### Code Block Processing

```python
from marktripy import parse_markdown, render_markdown

def process_code_blocks(ast, processor_func):
    """Apply processing to code blocks"""
    for node in ast.walk():
        if node.type == "code_block":
            language = node.attrs.get('lang', '')
            processor_func(node, language)
    return ast

def add_line_numbers(node, language):
    """Add line numbers to code blocks"""
    if hasattr(node, 'content') and node.content:
        lines = node.content.split('\n')
        numbered_lines = [
            f"{i+1:3d}: {line}" 
            for i, line in enumerate(lines)
        ]
        node.content = '\n'.join(numbered_lines)

def highlight_keywords(node, language):
    """Simple keyword highlighting for demonstration"""
    if language == "python" and hasattr(node, 'content'):
        keywords = ['def', 'class', 'import', 'from', 'if', 'else', 'for', 'while']
        content = node.content
        for keyword in keywords:
            content = content.replace(
                f' {keyword} ', 
                f' **{keyword}** '
            )
        node.content = content

def validate_code_syntax(ast):
    """Basic syntax validation for code blocks"""
    issues = []
    
    for node in ast.walk():
        if node.type == "code_block":
            language = node.attrs.get('lang', '')
            content = getattr(node, 'content', '')
            
            if language == "python":
                # Basic Python syntax check
                try:
                    compile(content, '<string>', 'exec')
                except SyntaxError as e:
                    issues.append(f"Python syntax error: {e}")
    
    return issues

# Example usage
markdown = """
Here's some Python code:

```python
def hello_world():
    print("Hello, World!")
    return True

if __name__ == "__main__":
    hello_world()
```

And some JavaScript:

```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);
}
```
"""

ast = parse_markdown(markdown)

# Validate syntax
issues = validate_code_syntax(ast)
if issues:
    print("Code issues found:", issues)

# Process code blocks
ast = process_code_blocks(ast, add_line_numbers)
result = render_markdown(ast)
print(result)
```

## Complex Document Restructuring

### Document Outline Manipulation

```python
from marktripy import parse_markdown, render_markdown

def extract_sections(ast):
    """Extract document sections based on headings"""
    sections = []
    current_section = None
    
    for node in ast.walk():
        if node.type == "heading":
            # Start new section
            if current_section:
                sections.append(current_section)
            
            current_section = {
                'heading': node,
                'content': [],
                'level': node.level
            }
        elif current_section and node != current_section['heading']:
            current_section['content'].append(node)
    
    if current_section:
        sections.append(current_section)
    
    return sections

def reorder_sections(ast, new_order):
    """Reorder sections according to specified order"""
    sections = extract_sections(ast)
    
    # Build new document with reordered sections
    new_children = []
    for section_index in new_order:
        if 0 <= section_index < len(sections):
            section = sections[section_index]
            new_children.append(section['heading'])
            new_children.extend(section['content'])
    
    ast.children = new_children
    return ast

def create_table_of_contents(ast, max_level=3):
    """Generate a table of contents from headings"""
    toc_items = []
    
    for node in ast.walk():
        if node.type == "heading" and node.level <= max_level:
            text = extract_text_content(node)
            level = node.level
            anchor = node.attrs.get('id') or slugify(text)
            
            toc_items.append({
                'text': text,
                'level': level,
                'anchor': anchor
            })
    
    # Build TOC markdown
    toc_markdown = "## Table of Contents\n\n"
    for item in toc_items:
        indent = "  " * (item['level'] - 1)
        toc_markdown += f"{indent}- [{item['text']}](#{item['anchor']})\n"
    
    # Parse TOC and insert at beginning
    toc_ast = parse_markdown(toc_markdown)
    
    # Insert TOC after first heading if exists
    insert_index = 1 if ast.children and ast.children[0].type == "heading" else 0
    ast.children[insert_index:insert_index] = toc_ast.children
    
    return ast

# Example usage
markdown = """
# Main Document

Some introduction text.

## Section A

Content for section A.

### Subsection A.1

More content.

## Section B

Content for section B.

## Section C

Final section content.
"""

ast = parse_markdown(markdown)

# Add IDs to headings first
ast = add_heading_ids(ast)

# Create table of contents
ast = create_table_of_contents(ast)

result = render_markdown(ast)
print(result)
```

### Content Filtering and Extraction

```python
from marktripy import parse_markdown, render_markdown

def filter_content(ast, filter_func):
    """Remove nodes that don't pass the filter function"""
    def filter_children(node):
        if hasattr(node, 'children'):
            node.children = [
                child for child in node.children 
                if filter_func(child)
            ]
            # Recursively filter children
            for child in node.children:
                filter_children(child)
    
    filter_children(ast)
    return ast

def extract_content_by_type(ast, node_types):
    """Extract only specific types of content"""
    extracted = []
    
    for node in ast.walk():
        if node.type in node_types:
            extracted.append(node)
    
    return extracted

def remove_empty_paragraphs(ast):
    """Remove paragraphs with no meaningful content"""
    def is_empty_paragraph(node):
        if node.type != "paragraph":
            return False
        
        text_content = extract_text_content(node).strip()
        return len(text_content) == 0
    
    return filter_content(ast, lambda node: not is_empty_paragraph(node))

def extract_summary(ast, max_paragraphs=3):
    """Extract first few paragraphs as document summary"""
    paragraphs = []
    
    for node in ast.walk():
        if node.type == "paragraph":
            paragraphs.append(node)
            if len(paragraphs) >= max_paragraphs:
                break
    
    # Create new document with summary
    summary_ast = {
        'type': 'document',
        'children': paragraphs,
        'attrs': {}
    }
    
    return summary_ast

# Example usage
markdown = """
# Long Document

This is the introduction paragraph with important information.

This is the second paragraph with more details.

## Section 1

This paragraph is in a section.



## Section 2

Another paragraph here.

> This is a blockquote.

Final paragraph of the document.
"""

ast = parse_markdown(markdown)

# Remove empty paragraphs
ast = remove_empty_paragraphs(ast)

# Extract summary
summary = extract_summary(ast, max_paragraphs=2)
summary_text = render_markdown(summary)
print("Summary:", summary_text)

# Extract only headings and paragraphs
content_only = filter_content(
    ast, 
    lambda node: node.type in ['heading', 'paragraph']
)
result = render_markdown(content_only)
print("Filtered content:", result)
```

## Performance Optimization

### Efficient Node Traversal

```python
from marktripy import parse_markdown

def efficient_find(ast, predicate, max_results=None):
    """Efficiently find nodes with early termination"""
    results = []
    
    for node in ast.walk():
        if predicate(node):
            results.append(node)
            if max_results and len(results) >= max_results:
                break
    
    return results

def batch_transform(ast, transformations):
    """Apply multiple transformations in a single pass"""
    for node in ast.walk():
        for transform_func in transformations:
            transform_func(node)
    return ast

# Example: Apply multiple transformations efficiently
def uppercase_text(node):
    if node.type == "text" and node.content:
        node.content = node.content.upper()

def add_emphasis_class(node):
    if node.type == "emphasis":
        node.attrs = node.attrs or {}
        node.attrs['class'] = 'italic'

def mark_external_links(node):
    if node.type == "link":
        href = node.attrs.get('href', '')
        if href.startswith('http'):
            node.attrs = node.attrs or {}
            node.attrs['class'] = 'external'

# Apply all transformations in single pass
ast = parse_markdown(markdown)
ast = batch_transform(ast, [
    uppercase_text,
    add_emphasis_class,
    mark_external_links
])
```

## Error Handling and Validation

```python
from marktripy import parse_markdown

def safe_transform(ast, transform_func):
    """Apply transformation with error handling"""
    try:
        return transform_func(ast)
    except Exception as e:
        print(f"Transformation failed: {e}")
        return ast

def validate_ast_structure(ast):
    """Validate AST structure integrity"""
    issues = []
    
    for node in ast.walk():
        # Check required attributes
        if not hasattr(node, 'type'):
            issues.append("Node missing 'type' attribute")
        
        # Check heading levels
        if node.type == "heading":
            if not hasattr(node, 'level') or not 1 <= node.level <= 6:
                issues.append(f"Invalid heading level: {getattr(node, 'level', 'missing')}")
        
        # Check link attributes
        if node.type == "link":
            if not hasattr(node, 'attrs') or 'href' not in node.attrs:
                issues.append("Link missing href attribute")
    
    return issues

# Example usage with validation
ast = parse_markdown(markdown)

# Validate before transformation
issues = validate_ast_structure(ast)
if issues:
    print("Pre-transformation issues:", issues)

# Apply transformation safely
ast = safe_transform(ast, add_heading_ids)

# Validate after transformation
issues = validate_ast_structure(ast)
if issues:
    print("Post-transformation issues:", issues)
```

## Next Steps

You now have the tools for powerful AST manipulation. Next, explore:

1. **[Extensions System](extensions.md)** - Create custom syntax
2. **[Transformers](transformers.md)** - Use built-in transformation utilities
3. **[Performance](performance.md)** - Optimize for large documents
4. **[CLI Usage](cli.md)** - Apply transformations via command line

The key to effective AST manipulation is understanding the document structure and applying transformations systematically while preserving document integrity.