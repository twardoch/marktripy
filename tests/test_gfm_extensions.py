# this_file: tests/test_gfm_extensions.py
"""Tests for GitHub Flavored Markdown extensions."""

import pytest

from marktripy.core.parser import ParserRegistry
from marktripy.parsers.markdown_it import MarkdownItParser  # Import to register
from marktripy.renderers.html import HTMLRenderer
from marktripy.renderers.markdown import MarkdownRenderer
from marktripy.extensions.strikethrough import StrikethroughExtension, Strikethrough
from marktripy.extensions.tasklist import TaskListExtension
from marktripy.extensions.gfm import GFMExtension
from marktripy.extensions.base import ExtensionManager
from marktripy.core.ast import ListItem


class TestStrikethroughExtension:
    """Test strikethrough extension functionality."""

    def test_simple_strikethrough(self):
        """Test simple strikethrough parsing."""
        parser = ParserRegistry.create("markdown-it", config={"preset": "default"})
        ext_manager = ExtensionManager()
        ext_manager.register(StrikethroughExtension())
        
        text = "This is ~~deleted~~ text."
        ast = parser.parse(text)
        ast = ext_manager.apply_ast_transformations(ast)
        
        # Check that Strikethrough nodes were created
        strike_nodes = [n for n in ast.walk() if isinstance(n, Strikethrough)]
        assert len(strike_nodes) == 1
        assert strike_nodes[0].children[0].content == "deleted"

    def test_strikethrough_html_rendering(self):
        """Test HTML rendering of strikethrough."""
        parser = ParserRegistry.create("markdown-it", config={"preset": "default"})
        renderer = HTMLRenderer()
        ext_manager = ExtensionManager()
        ext_manager.register(StrikethroughExtension())
        ext_manager.apply_renderer_extensions(renderer, "html")
        
        text = "This is ~~strikethrough~~ text."
        ast = parser.parse(text)
        ast = ext_manager.apply_ast_transformations(ast)
        html = renderer.render(ast)
        
        assert "<del>strikethrough</del>" in html

    def test_strikethrough_markdown_rendering(self):
        """Test Markdown rendering of strikethrough."""
        parser = ParserRegistry.create("markdown-it", config={"preset": "default"})
        renderer = MarkdownRenderer()
        ext_manager = ExtensionManager()
        ext_manager.register(StrikethroughExtension())
        ext_manager.apply_renderer_extensions(renderer, "markdown")
        
        text = "Text with ~~strikethrough~~."
        ast = parser.parse(text)
        ast = ext_manager.apply_ast_transformations(ast)
        md = renderer.render(ast)
        
        assert "~~strikethrough~~" in md

    def test_multiple_strikethrough(self):
        """Test multiple strikethrough in one line."""
        parser = ParserRegistry.create("markdown-it", config={"preset": "default"})
        ext_manager = ExtensionManager()
        ext_manager.register(StrikethroughExtension())
        
        text = "~~First~~ and ~~second~~ strikethrough."
        ast = parser.parse(text)
        ast = ext_manager.apply_ast_transformations(ast)
        
        strike_nodes = [n for n in ast.walk() if isinstance(n, Strikethrough)]
        assert len(strike_nodes) == 2


class TestTaskListExtension:
    """Test task list extension functionality."""

    def test_task_list_parsing(self):
        """Test task list item detection."""
        parser = ParserRegistry.create("markdown-it", config={"preset": "default"})
        ext_manager = ExtensionManager()
        ext_manager.register(TaskListExtension())
        
        text = """- [ ] Unchecked item
- [x] Checked item
- Regular item"""
        
        ast = parser.parse(text)
        ast = ext_manager.apply_ast_transformations(ast)
        
        # Find list items
        list_items = [n for n in ast.walk() if isinstance(n, ListItem)]
        assert len(list_items) == 3
        
        # Check task attributes
        assert list_items[0].get_attr('task') is True
        assert list_items[0].get_attr('checked') is False
        assert list_items[1].get_attr('task') is True
        assert list_items[1].get_attr('checked') is True
        assert list_items[2].get_attr('task') is None

    def test_task_list_html_rendering(self):
        """Test HTML rendering of task lists."""
        parser = ParserRegistry.create("markdown-it", config={"preset": "default"})
        renderer = HTMLRenderer()
        ext_manager = ExtensionManager()
        ext_manager.register(TaskListExtension())
        ext_manager.apply_renderer_extensions(renderer, "html")
        
        text = """- [ ] Todo item
- [x] Done item"""
        
        ast = parser.parse(text)
        ast = ext_manager.apply_ast_transformations(ast)
        html = renderer.render(ast)
        
        assert '<input type="checkbox" disabled>' in html
        assert '<input type="checkbox" disabled checked>' in html

    def test_task_list_markdown_rendering(self):
        """Test Markdown rendering of task lists."""
        parser = ParserRegistry.create("markdown-it", config={"preset": "default"})
        renderer = MarkdownRenderer()
        ext_manager = ExtensionManager()
        ext_manager.register(TaskListExtension())
        ext_manager.apply_renderer_extensions(renderer, "markdown")
        
        text = """- [ ] Task 1
- [x] Task 2"""
        
        ast = parser.parse(text)
        ast = ext_manager.apply_ast_transformations(ast)
        md = renderer.render(ast)
        
        assert "[ ] Task 1" in md
        assert "[x] Task 2" in md

    def test_nested_task_lists(self):
        """Test nested task lists."""
        parser = ParserRegistry.create("markdown-it", config={"preset": "default"})
        ext_manager = ExtensionManager()
        ext_manager.register(TaskListExtension())
        
        text = """- [ ] Parent task
  - [x] Subtask 1
  - [ ] Subtask 2"""
        
        ast = parser.parse(text)
        ast = ext_manager.apply_ast_transformations(ast)
        
        # Find all task items
        task_items = [n for n in ast.walk() if isinstance(n, ListItem) and n.get_attr('task')]
        assert len(task_items) == 3


class TestGFMBundle:
    """Test the complete GFM extension bundle."""

    def test_gfm_bundle_metadata(self):
        """Test GFM bundle metadata."""
        ext = GFMExtension()
        assert ext.get_name() == "gfm"
        assert "GitHub" in ext.get_description()

    def test_gfm_combined_features(self):
        """Test multiple GFM features together."""
        parser = ParserRegistry.create("markdown-it", config={"preset": "default", "enable": ["strikethrough", "table"]})
        renderer = HTMLRenderer()
        ext_manager = ExtensionManager()
        ext_manager.register(GFMExtension())
        ext_manager.apply_renderer_extensions(renderer, "html")
        
        text = """# GitHub Flavored Markdown

This has ~~strikethrough~~ text.

## Task List
- [x] Completed task with ~~old text~~
- [ ] Pending task
- Regular item

| Feature | Supported |
|---------|-----------|
| Tables  | Yes       |
| Strike  | Yes       |"""
        
        ast = parser.parse(text)
        ast = ext_manager.apply_ast_transformations(ast)
        html = renderer.render(ast)
        
        # Check all features are rendered
        assert "<del>strikethrough</del>" in html
        assert '<input type="checkbox" disabled checked>' in html
        assert '<input type="checkbox" disabled>' in html
        assert "<table>" in html
        assert "<th>Feature</th>" in html

    def test_gfm_roundtrip(self):
        """Test round-trip conversion with GFM features."""
        parser = ParserRegistry.create("markdown-it", config={"preset": "default"})
        md_renderer = MarkdownRenderer()
        ext_manager = ExtensionManager()
        ext_manager.register(GFMExtension())
        ext_manager.apply_renderer_extensions(md_renderer, "markdown")
        
        original = """Text with ~~strikethrough~~.

- [x] Completed task
- [ ] Pending task"""
        
        ast = parser.parse(original)
        ast = ext_manager.apply_ast_transformations(ast)
        result = md_renderer.render(ast)
        
        assert "~~strikethrough~~" in result
        assert "[x] Completed" in result
        assert "[ ] Pending" in result