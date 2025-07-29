# this_file: marktripy/extensions/gfm.py
"""GitHub Flavored Markdown (GFM) extension bundle for marktripy.

This extension provides a convenient way to enable all GFM features at once:
- Tables (already built-in)
- Strikethrough
- Task lists
- Autolinks
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from marktripy.core.ast import ASTNode
from marktripy.extensions.base import Extension
from marktripy.extensions.strikethrough import StrikethroughExtension
from marktripy.extensions.tasklist import TaskListExtension


class GFMExtension(Extension):
    """Bundle extension that enables all GitHub Flavored Markdown features."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize GFM extension bundle.

        Args:
            config: Configuration options
        """
        super().__init__(config)

        # Initialize sub-extensions
        self.strikethrough = StrikethroughExtension(config)
        self.tasklist = TaskListExtension(config)
        # Note: Tables are already supported in the base parser
        # TODO: Add autolink extension when implemented

    def get_name(self) -> str:
        """Get extension name."""
        return "gfm"

    def get_description(self) -> str:
        """Get extension description."""
        return "GitHub Flavored Markdown support (tables, strikethrough, task lists)"

    def get_dependencies(self) -> list[str]:
        """Get dependencies."""
        # This bundle doesn't depend on other extensions,
        # but it contains sub-extensions
        return []

    def register_inline_rule(self, parser: Any) -> None:
        """Register inline parsing rules.

        Args:
            parser: Parser to register rules with
        """
        # Let sub-extensions register their rules
        self.strikethrough.register_inline_rule(parser)
        logger.debug("Registered GFM inline rules")

    def transform_ast(self, ast: ASTNode) -> ASTNode:
        """Transform AST with all GFM transformations.

        Args:
            ast: AST to transform

        Returns:
            Transformed AST
        """
        # Apply transformations in order
        ast = self.strikethrough.transform_ast(ast)
        return self.tasklist.transform_ast(ast)

    def register_html_renderer(self, renderer: Any) -> None:
        """Register HTML rendering methods.

        Args:
            renderer: HTML renderer to extend
        """
        self.strikethrough.register_html_renderer(renderer)
        self.tasklist.register_html_renderer(renderer)
        logger.debug("Registered GFM HTML renderers")

    def register_markdown_renderer(self, renderer: Any) -> None:
        """Register Markdown rendering methods.

        Args:
            renderer: Markdown renderer to extend
        """
        self.strikethrough.register_markdown_renderer(renderer)
        self.tasklist.register_markdown_renderer(renderer)
        logger.debug("Registered GFM Markdown renderers")

    def setup(self) -> None:
        """Perform setup for sub-extensions."""
        self.strikethrough.setup()
        self.tasklist.setup()
        logger.info("GFM extension bundle initialized")

    def teardown(self) -> None:
        """Perform teardown for sub-extensions."""
        self.strikethrough.teardown()
        self.tasklist.teardown()
