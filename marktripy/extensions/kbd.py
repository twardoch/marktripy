# this_file: marktripy/extensions/kbd.py
"""Keyboard key extension for marktripy.

Provides support for ++key++ syntax to render keyboard keys.
"""

from __future__ import annotations

import re
from typing import Any

from loguru import logger

from marktripy.core.ast import ASTNode, Text
from marktripy.extensions.base import Extension


class KeyboardKey(ASTNode):
    """AST node for keyboard keys."""

    def __init__(self, key: str):
        """Initialize keyboard key node.

        Args:
            key: The key text to display
        """
        super().__init__(type="keyboard_key", content=key)
        self.key = key


class KbdExtension(Extension):
    """Extension that adds support for ++key++ syntax."""

    def get_name(self) -> str:
        """Get extension name."""
        return "kbd"

    def get_description(self) -> str:
        """Get extension description."""
        return "Adds support for keyboard key notation using ++key++ syntax"

    def register_inline_rule(self, parser: Any) -> None:
        """Register inline parsing rule for ++key++ syntax.

        Args:
            parser: Parser to register rule with
        """
        # For now, we'll handle this in transform_ast since
        # markdown-it-py doesn't easily support custom inline rules
        # without modifying the parser internals
        logger.debug("KbdExtension will use AST transformation for ++key++ syntax")

    def transform_ast(self, ast: ASTNode) -> ASTNode:
        """Transform AST to convert kbd tokens to KeyboardKey nodes.

        Args:
            ast: AST to transform

        Returns:
            Transformed AST
        """
        # For parsers that don't support custom inline rules,
        # we can post-process text nodes to find ++key++ patterns
        self._transform_node(ast)
        return ast

    def _transform_node(self, node: ASTNode) -> list[ASTNode] | None:
        """Transform a node and its children, returning replacement nodes if needed.

        Args:
            node: Node to process

        Returns:
            List of replacement nodes, or None if no replacement needed
        """
        # First, transform all children
        new_children = []
        for child in node.children:
            result = self._transform_node(child)
            if result is not None:
                # Child was replaced with new nodes
                new_children.extend(result)
            else:
                # Keep original child
                new_children.append(child)

        # Update node's children if any were replaced
        if len(new_children) != len(node.children) or any(
            new_children[i] is not node.children[i] for i in range(len(new_children))
        ):
            node.children = new_children

        # Now check if this node itself needs transformation
        if isinstance(node, Text) and node.content:
            # Look for ++key++ patterns
            # Updated pattern to handle empty keys and be more flexible
            pattern = r"\+\+([^+]*)\+\+"
            parts = []
            last_end = 0

            for match in re.finditer(pattern, node.content):
                # Add text before the match
                if match.start() > last_end:
                    parts.append(Text(content=node.content[last_end : match.start()]))

                # Add keyboard key node
                parts.append(KeyboardKey(key=match.group(1)))
                last_end = match.end()

            # Add remaining text
            if last_end < len(node.content):
                parts.append(Text(content=node.content[last_end:]))

            # If we found any matches, return the replacement nodes
            if len(parts) > 1:
                return parts

        # No replacement needed
        return None

    def register_html_renderer(self, renderer: Any) -> None:
        """Register HTML rendering for keyboard keys.

        Args:
            renderer: HTML renderer to extend
        """

        def render_keyboard_key(node: KeyboardKey) -> str:
            """Render keyboard key as HTML."""
            # Escape HTML in the key text
            key = node.key.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            return f"<kbd>{key}</kbd>"

        # Register the render method
        renderer.render_keyboard_key = render_keyboard_key
        logger.debug("Registered kbd HTML renderer")

    def register_markdown_renderer(self, renderer: Any) -> None:
        """Register Markdown rendering for keyboard keys.

        Args:
            renderer: Markdown renderer to extend
        """

        def render_keyboard_key(node: KeyboardKey) -> str:
            """Render keyboard key back to Markdown."""
            # Escape any + characters in the key
            key = node.key.replace("+", "\\+")
            return f"++{key}++"

        # Register the render method
        renderer.render_keyboard_key = render_keyboard_key
        logger.debug("Registered kbd Markdown renderer")
