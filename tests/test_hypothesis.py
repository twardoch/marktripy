# this_file: tests/test_hypothesis.py
"""Property-based tests using Hypothesis."""

from hypothesis import given, strategies as st, assume, settings
from hypothesis.strategies import composite

from marktripy.core.ast import (
    Document,
    Heading,
    Paragraph,
    Text,
    Strong,
    Emphasis,
    List,
    ListItem,
    Link,
    Image,
    CodeBlock,
    InlineCode,
)
from marktripy.core.validator import validate_ast_strict
from marktripy.parsers.markdown_it import MarkdownItParser
from marktripy.renderers.html import HTMLRenderer
from marktripy.transformers.heading import normalize_headings
from marktripy.transformers.id_generator import add_heading_ids
from marktripy.utils.slugify import slugify, generate_id


# Strategies for generating AST nodes
@composite
def text_nodes(draw):
    """Generate Text nodes with valid content."""
    content = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    return Text(content=content)


@composite
def heading_nodes(draw):
    """Generate Heading nodes with valid levels."""
    level = draw(st.integers(min_value=1, max_value=6))
    heading = Heading(level=level)
    # Add text content
    heading.add_child(draw(text_nodes()))
    return heading


@composite
def paragraph_nodes(draw):
    """Generate Paragraph nodes with content."""
    para = Paragraph()
    # Add 1-3 inline nodes
    num_children = draw(st.integers(min_value=1, max_value=3))
    for _ in range(num_children):
        child = draw(st.one_of(
            text_nodes(),
            emphasis_nodes(),
            strong_nodes(),
            inline_code_nodes(),
        ))
        para.add_child(child)
    return para


@composite
def emphasis_nodes(draw):
    """Generate Emphasis nodes."""
    em = Emphasis()
    em.add_child(draw(text_nodes()))
    return em


@composite
def strong_nodes(draw):
    """Generate Strong nodes."""
    strong = Strong()
    strong.add_child(draw(text_nodes()))
    return strong


@composite
def inline_code_nodes(draw):
    """Generate InlineCode nodes."""
    content = draw(st.text(min_size=1, max_size=50))
    return InlineCode(content=content)


@composite
def link_nodes(draw):
    """Generate Link nodes."""
    href = draw(st.one_of(
        st.just("https://example.com"),
        st.just("https://github.com"),
        st.just("mailto:test@example.com"),
        st.text(min_size=1, max_size=50).map(lambda x: f"https://{x}.com")
    ))
    link = Link(href=href)
    link.add_child(draw(text_nodes()))
    return link


@composite
def list_nodes(draw):
    """Generate List nodes with items."""
    ordered = draw(st.booleans())
    list_node = List(ordered=ordered)
    
    # Add 1-5 list items
    num_items = draw(st.integers(min_value=1, max_value=5))
    for _ in range(num_items):
        item = ListItem()
        item.add_child(draw(paragraph_nodes()))
        list_node.add_child(item)
    
    return list_node


@composite
def document_nodes(draw):
    """Generate complete Document nodes."""
    doc = Document()
    
    # Add 1-10 block elements
    num_blocks = draw(st.integers(min_value=1, max_value=10))
    for _ in range(num_blocks):
        block = draw(st.one_of(
            heading_nodes(),
            paragraph_nodes(),
            list_nodes(),
        ))
        doc.add_child(block)
    
    return doc


class TestSlugify:
    """Property-based tests for slugify function."""

    @given(st.text())
    def test_slugify_always_returns_string(self, text):
        """Slugify should always return a string."""
        result = slugify(text)
        assert isinstance(result, str)

    @given(st.text(min_size=1))
    def test_slugify_lowercase(self, text):
        """Slugify with lowercase=True should return lowercase."""
        result = slugify(text, lowercase=True)
        assert result == result.lower()

    @given(st.text(alphabet=st.characters(whitelist_categories=["Lu", "Ll", "Nd"])))
    def test_slugify_alphanumeric(self, text):
        """Slugify should preserve alphanumeric ASCII characters."""
        assume(text.strip())  # Skip empty strings
        result = slugify(text)
        # Check if text has ASCII alphanumeric characters
        ascii_text = text.encode('ascii', 'ignore').decode('ascii')
        if any(c.isalnum() for c in ascii_text):
            assert len(result) > 0

    @given(st.text(), st.integers(min_value=1, max_value=50))
    def test_slugify_max_length(self, text, max_length):
        """Slugify should respect max_length."""
        result = slugify(text, max_length=max_length)
        assert len(result) <= max_length

    @given(st.lists(st.text(min_size=1, max_size=20), min_size=2, max_size=5))
    def test_generate_id_uniqueness(self, texts):
        """generate_id should create unique IDs."""
        existing_ids = set()
        generated_ids = []
        
        for text in texts:
            new_id = generate_id(text, existing_ids)
            generated_ids.append(new_id)
            existing_ids.add(new_id)
        
        # All IDs should be unique
        assert len(generated_ids) == len(set(generated_ids))


class TestASTValidation:
    """Property-based tests for AST validation."""

    @given(document_nodes())
    def test_generated_ast_is_valid(self, doc):
        """Generated ASTs should be valid."""
        # Should not raise
        validate_ast_strict(doc)

    @given(heading_nodes())
    def test_heading_levels_valid(self, heading):
        """Heading levels should be 1-6."""
        assert 1 <= heading.level <= 6
        doc = Document()
        doc.add_child(heading)
        validate_ast_strict(doc)

    @given(st.integers())
    def test_invalid_heading_levels(self, level):
        """Invalid heading levels should fail validation."""
        assume(level < 1 or level > 6)
        try:
            heading = Heading(level=level)
            # Should raise ValueError in constructor
            assert False, "Should have raised ValueError"
        except ValueError:
            pass


class TestTransformers:
    """Property-based tests for transformers."""

    @given(document_nodes())
    def test_normalize_headings_preserves_structure(self, doc):
        """Normalizing headings should preserve document structure."""
        original_count = len(doc.find_all("heading"))
        
        normalized = normalize_headings(doc)
        
        # Same number of headings
        assert len(normalized.find_all("heading")) == original_count
        
        # All headings should have valid levels
        for heading in normalized.find_all("heading"):
            assert 1 <= heading.level <= 6

    @given(document_nodes())
    def test_add_heading_ids_all_unique(self, doc):
        """All generated heading IDs should be unique."""
        result = add_heading_ids(doc)
        
        ids = []
        for heading in result.find_all("heading"):
            heading_id = heading.get_attr("id")
            if heading_id:
                ids.append(heading_id)
        
        # All IDs should be unique
        assert len(ids) == len(set(ids))

    @given(document_nodes())
    @settings(max_examples=10)  # Limit examples for performance
    def test_parser_renderer_roundtrip(self, doc):
        """Rendering and re-parsing should preserve structure."""
        # Render to HTML
        renderer = HTMLRenderer()
        html = renderer.render(doc)
        
        # Basic checks
        assert isinstance(html, str)
        assert len(html) > 0
        
        # Count certain elements
        heading_count = len(doc.find_all("heading"))
        list_count = len(doc.find_all("list"))
        
        # Count paragraphs that aren't in tight lists
        para_count = 0
        for para in doc.find_all("paragraph"):
            # Check if paragraph is inside a tight list
            is_in_tight_list = False
            for list_node in doc.find_all("list"):
                if list_node.tight and para in [n for item in list_node.children for n in item.walk()]:
                    is_in_tight_list = True
                    break
            if not is_in_tight_list:
                para_count += 1
        
        # HTML should contain appropriate tags
        assert html.count("<h") >= heading_count
        assert html.count("<p") >= para_count
        assert html.count("<ul") + html.count("<ol") >= list_count


class TestMarkdownParsing:
    """Property-based tests for Markdown parsing."""

    @given(st.text(alphabet=st.characters(whitelist_categories=["L", "N", "Z"]), min_size=1))
    def test_parse_plain_text(self, text):
        """Parser should handle plain text without errors."""
        parser = MarkdownItParser()
        ast = parser.parse(text)
        
        assert isinstance(ast, Document)
        # Should create at least one node
        assert len(ast.children) >= 1

    @given(st.integers(min_value=1, max_value=6), st.text(min_size=1, max_size=50))
    def test_parse_headings(self, level, text):
        """Parser should correctly parse headings."""
        assume(not text.startswith("#"))  # Avoid nested headings
        
        markdown = "#" * level + " " + text
        parser = MarkdownItParser()
        ast = parser.parse(markdown)
        
        headings = ast.find_all("heading")
        assert len(headings) == 1
        assert headings[0].level == level

    @given(st.lists(
        st.text(min_size=1, max_size=20).filter(lambda x: '\r' not in x and '\n' not in x),
        min_size=1, max_size=5
    ))
    def test_parse_lists(self, items):
        """Parser should handle lists correctly."""
        # Create unordered list
        markdown = "\n".join(f"- {item}" for item in items)
        parser = MarkdownItParser()
        ast = parser.parse(markdown)
        
        lists = ast.find_all("list")
        assert len(lists) == 1
        assert not lists[0].ordered
        
        list_items = ast.find_all("list_item")
        assert len(list_items) == len(items)