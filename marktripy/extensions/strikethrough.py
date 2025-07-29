# this_file: marktripy/extensions/strikethrough.py
"""Strikethrough extension for marktripy.

Provides support for ~~strikethrough~~ syntax as used in GitHub Flavored Markdown.
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from marktripy.core.ast import ASTNode
from marktripy.extensions.base import Extension


class Strikethrough(ASTNode):
    """AST node for strikethrough text."""

    def __init__(self):
        """Initialize strikethrough node."""
        super().__init__(type="strikethrough")


class StrikethroughExtension(Extension):
    """Extension that adds support for ~~strikethrough~~ syntax."""

    def get_name(self) -> str:
        """Get extension name."""
        return "strikethrough"

    def get_description(self) -> str:
        """Get extension description."""
        return "Adds support for strikethrough text using ~~text~~ syntax"

    def register_inline_rule(self, parser: Any) -> None:
        """Register inline parsing rule for ~~text~~ syntax.

        Args:
            parser: Parser to register rule with
        """
        # For now, we'll handle this in transform_ast
        logger.debug("StrikethroughExtension will use AST transformation")

    def transform_ast(self, ast: ASTNode) -> ASTNode:
        """Transform AST to convert generic strikethrough nodes to Strikethrough nodes.

        Args:
            ast: AST to transform

        Returns:
            Transformed AST
        """
        self._transform_strikethrough_nodes(ast)
        return ast

    def _transform_strikethrough_nodes(self, node: ASTNode) -> None:
        """Recursively transform generic strikethrough nodes to our Strikethrough type.

        Args:
            node: Node to process
        """
        # Check if this is a generic strikethrough node created by the parser
        if node.type == "strikethrough" and not isinstance(node, Strikethrough):
            # Create a proper Strikethrough node
            new_node = Strikethrough()
            # Copy children
            new_node.children = node.children
            # Copy attributes
            new_node.attrs = node.attrs
            new_node.meta = node.meta

            # Replace this node in its parent
            if hasattr(node, "parent") and node.parent:
                try:
                    index = node.parent.children.index(node)
                    node.parent.children[index] = new_node
                except (ValueError, AttributeError):
                    pass

        # Process children
        for i, child in enumerate(list(node.children)):
            if child.type == "strikethrough" and not isinstance(child, Strikethrough):
                # Replace with proper Strikethrough node
                new_node = Strikethrough()
                new_node.children = child.children
                new_node.attrs = child.attrs
                new_node.meta = child.meta
                node.children[i] = new_node
                self._transform_strikethrough_nodes(new_node)
            else:
                self._transform_strikethrough_nodes(child)

    def register_html_renderer(self, renderer: Any) -> None:
        """Register HTML rendering for strikethrough.

        Args:
            renderer: HTML renderer to extend
        """

        def render_strikethrough(node: Strikethrough) -> str:
            """Render strikethrough as HTML."""
            content = renderer.render_children(node)
            return f"<del>{content}</del>"

        # Register the render method
        renderer.render_strikethrough = render_strikethrough
        logger.debug("Registered strikethrough HTML renderer")

    def register_markdown_renderer(self, renderer: Any) -> None:
        """Register Markdown rendering for strikethrough.

        Args:
            renderer: Markdown renderer to extend
        """

        def render_strikethrough(node: Strikethrough) -> str:
            """Render strikethrough back to Markdown."""
            content = renderer.render_children(node)
            return f"~~{content}~~"

        # Register the render method
        renderer.render_strikethrough = render_strikethrough
        logger.debug("Registered strikethrough Markdown renderer")
