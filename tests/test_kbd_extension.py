# this_file: tests/test_kbd_extension.py
"""Tests for the keyboard key extension."""

import pytest

from marktripy.core.parser import ParserRegistry
from marktripy.parsers.markdown_it import MarkdownItParser  # Import to register
from marktripy.renderers.html import HTMLRenderer
from marktripy.renderers.markdown import MarkdownRenderer
from marktripy.extensions.kbd import KbdExtension, KeyboardKey
from marktripy.extensions.base import ExtensionManager


class TestKbdExtension:
    """Test keyboard key extension functionality."""

    def test_extension_metadata(self):
        """Test extension metadata."""
        ext = KbdExtension()
        assert ext.get_name() == "kbd"
        assert "keyboard" in ext.get_description().lower()
        assert ext.get_dependencies() == []

    def test_simple_kbd(self):
        """Test simple keyboard key parsing."""
        # Create parser with extension
        parser = ParserRegistry.create("markdown-it")
        ext_manager = ExtensionManager()
        ext_manager.register(KbdExtension())
        ext_manager.apply_parser_extensions(parser)
        
        # Parse text with kbd syntax
        text = "Press ++Ctrl++ and ++Alt++ together."
        ast = parser.parse(text)
        
        # Transform AST
        ast = ext_manager.apply_ast_transformations(ast)
        
        # Check that KeyboardKey nodes were created
        kbd_nodes = [n for n in ast.walk() if isinstance(n, KeyboardKey)]
        assert len(kbd_nodes) == 2
        assert kbd_nodes[0].key == "Ctrl"
        assert kbd_nodes[1].key == "Alt"

    def test_kbd_html_rendering(self):
        """Test HTML rendering of keyboard keys."""
        # Setup
        parser = ParserRegistry.create("markdown-it")
        renderer = HTMLRenderer()
        ext_manager = ExtensionManager()
        ext_manager.register(KbdExtension())
        ext_manager.apply_parser_extensions(parser)
        ext_manager.apply_renderer_extensions(renderer, "html")
        
        # Parse and render
        text = "Press ++Enter++ to continue."
        ast = parser.parse(text)
        ast = ext_manager.apply_ast_transformations(ast)
        html = renderer.render(ast)
        
        assert "<kbd>Enter</kbd>" in html
        assert "<p>" in html

    def test_kbd_markdown_rendering(self):
        """Test Markdown rendering of keyboard keys."""
        # Setup
        parser = ParserRegistry.create("markdown-it")
        renderer = MarkdownRenderer()
        ext_manager = ExtensionManager()
        ext_manager.register(KbdExtension())
        ext_manager.apply_parser_extensions(parser)
        ext_manager.apply_renderer_extensions(renderer, "markdown")
        
        # Parse and render
        text = "Press ++Space++ to jump."
        ast = parser.parse(text)
        ast = ext_manager.apply_ast_transformations(ast)
        md = renderer.render(ast)
        
        assert "++Space++" in md

    def test_multiple_kbd_in_line(self):
        """Test multiple keyboard keys in one line."""
        parser = ParserRegistry.create("markdown-it")
        ext_manager = ExtensionManager()
        ext_manager.register(KbdExtension())
        ext_manager.apply_parser_extensions(parser)
        
        text = "Use ++Ctrl++++C++ to copy and ++Ctrl++++V++ to paste."
        ast = parser.parse(text)
        ast = ext_manager.apply_ast_transformations(ast)
        
        kbd_nodes = [n for n in ast.walk() if isinstance(n, KeyboardKey)]
        assert len(kbd_nodes) == 4
        assert kbd_nodes[0].key == "Ctrl"
        assert kbd_nodes[1].key == "C"
        assert kbd_nodes[2].key == "Ctrl"
        assert kbd_nodes[3].key == "V"

    def test_kbd_with_special_chars(self):
        """Test keyboard keys with special characters."""
        parser = ParserRegistry.create("markdown-it")
        renderer = HTMLRenderer()
        ext_manager = ExtensionManager()
        ext_manager.register(KbdExtension())
        ext_manager.apply_parser_extensions(parser)
        ext_manager.apply_renderer_extensions(renderer, "html")
        
        text = "Press ++<++ and ++>++ for navigation."
        ast = parser.parse(text)
        ast = ext_manager.apply_ast_transformations(ast)
        html = renderer.render(ast)
        
        # Check HTML escaping
        assert "<kbd>&lt;</kbd>" in html
        assert "<kbd>&gt;</kbd>" in html

    def test_nested_formatting(self):
        """Test kbd syntax within other formatting."""
        parser = ParserRegistry.create("markdown-it")
        ext_manager = ExtensionManager()
        ext_manager.register(KbdExtension())
        ext_manager.apply_parser_extensions(parser)
        
        text = "**Important:** Press ++Delete++ carefully!"
        ast = parser.parse(text)
        ast = ext_manager.apply_ast_transformations(ast)
        
        # Check structure
        kbd_nodes = [n for n in ast.walk() if isinstance(n, KeyboardKey)]
        assert len(kbd_nodes) == 1
        assert kbd_nodes[0].key == "Delete"

    def test_incomplete_kbd_syntax(self):
        """Test incomplete kbd syntax is not parsed."""
        parser = ParserRegistry.create("markdown-it")
        ext_manager = ExtensionManager()
        ext_manager.register(KbdExtension())
        ext_manager.apply_parser_extensions(parser)
        
        text = "This ++is not complete"
        ast = parser.parse(text)
        ast = ext_manager.apply_ast_transformations(ast)
        
        # Should not create any KeyboardKey nodes
        kbd_nodes = [n for n in ast.walk() if isinstance(n, KeyboardKey)]
        assert len(kbd_nodes) == 0

    def test_empty_kbd(self):
        """Test empty kbd syntax."""
        parser = ParserRegistry.create("markdown-it")
        ext_manager = ExtensionManager()
        ext_manager.register(KbdExtension())
        ext_manager.apply_parser_extensions(parser)
        
        text = "This ++++ is empty"
        ast = parser.parse(text)
        ast = ext_manager.apply_ast_transformations(ast)
        
        # Should create an empty kbd node
        kbd_nodes = [n for n in ast.walk() if isinstance(n, KeyboardKey)]
        assert len(kbd_nodes) == 1
        assert kbd_nodes[0].key == ""

    def test_kbd_roundtrip(self):
        """Test round-trip conversion with kbd extension."""
        parser = ParserRegistry.create("markdown-it")
        md_renderer = MarkdownRenderer()
        ext_manager = ExtensionManager()
        ext_manager.register(KbdExtension())
        ext_manager.apply_parser_extensions(parser)
        ext_manager.apply_renderer_extensions(md_renderer, "markdown")
        
        original = "Press ++Esc++ to exit or ++F1++ for help."
        
        # Parse
        ast = parser.parse(original)
        ast = ext_manager.apply_ast_transformations(ast)
        
        # Render back to Markdown
        result = md_renderer.render(ast)
        
        assert "++Esc++" in result
        assert "++F1++" in result

    def test_kbd_with_plus_sign(self):
        """Test keyboard key containing plus sign."""
        parser = ParserRegistry.create("markdown-it")
        md_renderer = MarkdownRenderer()
        ext_manager = ExtensionManager()
        ext_manager.register(KbdExtension())
        ext_manager.apply_parser_extensions(parser)
        ext_manager.apply_renderer_extensions(md_renderer, "markdown")
        
        # Note: This is a limitation - can't have literal + in kbd
        text = "Press ++Shift++++Equal++ for plus sign."
        ast = parser.parse(text)
        ast = ext_manager.apply_ast_transformations(ast)
        
        kbd_nodes = [n for n in ast.walk() if isinstance(n, KeyboardKey)]
        assert len(kbd_nodes) == 2  # Shift and Equal
        
        # Render back
        result = md_renderer.render(ast)
        assert "++Shift++" in result
        assert "++Equal++" in result