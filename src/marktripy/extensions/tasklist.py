# this_file: marktripy/extensions/tasklist.py
"""Task list extension for marktripy.

Provides support for GitHub-style task lists:
- [ ] Unchecked task
- [x] Checked task
"""

from __future__ import annotations

import re
from typing import Any

from loguru import logger

from marktripy.core.ast import ASTNode, ListItem, Text
from marktripy.extensions.base import Extension


class TaskListExtension(Extension):
    """Extension that adds support for task list syntax."""

    def get_name(self) -> str:
        """Get extension name."""
        return "tasklist"

    def get_description(self) -> str:
        """Get extension description."""
        return "Adds support for GitHub-style task lists with checkboxes"

    def transform_ast(self, ast: ASTNode) -> ASTNode:
        """Transform AST to add task list attributes to list items.

        Args:
            ast: AST to transform

        Returns:
            Transformed AST
        """
        self._transform_list_items(ast)
        return ast

    def _transform_list_items(self, node: ASTNode) -> None:
        """Recursively transform list items to detect task list syntax.

        Args:
            node: Node to process
        """
        if isinstance(node, ListItem) and node.children and len(node.children) > 0:
            # Check if the first child contains task list syntax
            first_child = node.children[0]

            # Check if it's a paragraph or text node
            if hasattr(first_child, "children") and first_child.children:
                text_node = first_child.children[0]
            elif isinstance(first_child, Text):
                text_node = first_child
            else:
                text_node = None

            if text_node and isinstance(text_node, Text) and text_node.content:
                # Look for task list pattern at the start
                match = re.match(r"^\[([ xX])\]\s+(.*)$", text_node.content)
                if match:
                    # It's a task list item
                    checked = match.group(1).lower() == "x"
                    remaining_text = match.group(2)

                    # Set task list attributes
                    node.set_attr("task", True)
                    node.set_attr("checked", checked)

                    # Update the text content
                    text_node.content = remaining_text

        # Process children
        for child in node.children:
            self._transform_list_items(child)

    def register_html_renderer(self, renderer: Any) -> None:
        """Register HTML rendering for task lists.

        Args:
            renderer: HTML renderer to extend
        """
        # Store the original render_list_item method
        original_render_list_item = renderer.render_list_item

        def render_list_item(node: ListItem) -> str:
            """Render list item with task list support."""
            if node.get_attr("task"):
                # It's a task list item
                checked = node.get_attr("checked", False)
                checkbox = f'<input type="checkbox" disabled{"" if not checked else " checked"}>'

                # Render children
                content = renderer.render_children(node)

                # Wrap in list item with checkbox
                return f"<li>{checkbox} {content}</li>"
            # Regular list item
            return original_render_list_item(node)

        # Replace the render method
        renderer.render_list_item = render_list_item
        logger.debug("Registered task list HTML renderer")

    def register_markdown_renderer(self, renderer: Any) -> None:
        """Register Markdown rendering for task lists.

        Args:
            renderer: Markdown renderer to extend
        """
        # Store the original render_list_item method
        original_render_list_item = renderer.render_list_item

        def render_list_item(node: ListItem) -> str:
            """Render list item with task list support."""
            if node.get_attr("task"):
                # It's a task list item
                checked = node.get_attr("checked", False)
                checkbox = "[x]" if checked else "[ ]"

                # Render children
                content = renderer.render_children(node)

                # Strip extra newlines for tight lists
                if renderer.context.tight_list:
                    content = content.strip()

                # Prepend checkbox
                return f"{checkbox} {content}"
            # Regular list item
            return original_render_list_item(node)

        # Replace the render method
        renderer.render_list_item = render_list_item
        logger.debug("Registered task list Markdown renderer")
