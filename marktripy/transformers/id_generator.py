# this_file: marktripy/transformers/id_generator.py
"""ID generator transformer for marktripy."""

from __future__ import annotations

from typing import Any

from loguru import logger

from marktripy.core.ast import ASTNode, Document, Heading
from marktripy.transformers.base import Transformer
from marktripy.utils.slugify import IDGenerator, extract_text


class IDGeneratorTransformer(Transformer):
    """Adds IDs to headings in an AST.

    Generates URL-friendly IDs from heading text content,
    ensuring uniqueness across the document.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize ID generator transformer.

        Args:
            config: Transformer configuration with options:
                - prefix: Prefix for generated IDs
                - separator: Separator character (default: '-')
                - overwrite: Whether to overwrite existing IDs (default: False)
                - target_elements: List of element types to add IDs to (default: ['heading'])
        """
        super().__init__(config)

        self.prefix = self.config.get("prefix", "")
        self.separator = self.config.get("separator", "-")
        self.overwrite = self.config.get("overwrite", False)
        self.target_elements = self.config.get("target_elements", ["heading"])

        # Initialize ID generator
        self.id_generator = IDGenerator(prefix=self.prefix, separator=self.separator)

    def get_description(self) -> str:
        """Get transformer description.

        Returns:
            Description of what this transformer does
        """
        targets = ", ".join(self.target_elements)
        return f"Generates unique IDs for {targets} elements"

    def transform(self, ast: Document) -> Document:
        """Transform the AST by adding IDs.

        Args:
            ast: The AST to transform

        Returns:
            Transformed AST
        """
        # Reset ID generator for each transform
        self.id_generator.reset()

        # First pass: collect existing IDs
        if not self.overwrite:
            self._collect_existing_ids(ast)

        # Second pass: add IDs
        return super().transform(ast)

    def visit(self, node: ASTNode) -> ASTNode | None:
        """Visit a node and potentially add an ID.

        Args:
            node: The node to visit

        Returns:
            The node (with ID added if applicable)
        """
        # Check if this node type should get an ID
        if node.type in self.target_elements:
            self._add_id_to_node(node)

        # Continue with default visiting
        return super().visit(node)

    def visit_heading(self, node: Heading) -> Heading:
        """Visit a heading node.

        Args:
            node: The heading to process

        Returns:
            The heading with ID added
        """
        if "heading" in self.target_elements:
            self._add_id_to_node(node)

        # Visit children
        self.generic_visit(node)
        return node

    def _add_id_to_node(self, node: ASTNode) -> None:
        """Add an ID to a node if needed.

        Args:
            node: The node to add ID to
        """
        # Check if node already has an ID
        existing_id = node.get_attr("id")
        if existing_id and not self.overwrite:
            logger.debug(f"Keeping existing ID: {existing_id}")
            return

        # Extract text content for ID generation
        text = extract_text(node)
        if not text:
            logger.warning(f"No text content for ID generation in {node.type}")
            return

        # Generate and set ID
        new_id = self.id_generator.generate(text)
        node.set_attr("id", new_id)
        logger.debug(f"Generated ID '{new_id}' for {node.type}")

    def _collect_existing_ids(self, node: ASTNode) -> None:
        """Collect existing IDs in the AST.

        Args:
            node: Node to search for IDs
        """
        # Check this node for an ID
        existing_id = node.get_attr("id")
        if existing_id:
            self.id_generator.used_ids.add(existing_id)
            logger.debug(f"Found existing ID: {existing_id}")

        # Check children
        for child in node.children:
            self._collect_existing_ids(child)


class HeadingIDGenerator(IDGeneratorTransformer):
    """Convenience class for adding IDs to headings only."""

    def __init__(self, prefix: str = "", overwrite: bool = False):
        """Initialize heading ID generator.

        Args:
            prefix: Prefix for generated IDs
            overwrite: Whether to overwrite existing IDs
        """
        super().__init__(
            {
                "prefix": prefix,
                "overwrite": overwrite,
                "target_elements": ["heading"],
            }
        )


class TableIDGenerator(IDGeneratorTransformer):
    """Convenience class for adding IDs to tables."""

    def __init__(self, prefix: str = "table", overwrite: bool = False):
        """Initialize table ID generator.

        Args:
            prefix: Prefix for generated IDs
            overwrite: Whether to overwrite existing IDs
        """
        super().__init__(
            {
                "prefix": prefix,
                "overwrite": overwrite,
                "target_elements": ["table"],
            }
        )


# Convenience functions
def add_heading_ids(ast: Document, prefix: str = "", overwrite: bool = False) -> Document:
    """Add IDs to all headings in the AST.

    Args:
        ast: The AST to transform
        prefix: Prefix for generated IDs
        overwrite: Whether to overwrite existing IDs

    Returns:
        Transformed AST
    """
    transformer = HeadingIDGenerator(prefix=prefix, overwrite=overwrite)
    return transformer.transform(ast)


def add_ids_to_elements(
    ast: Document, elements: list[str], prefix: str = "", overwrite: bool = False
) -> Document:
    """Add IDs to specified element types.

    Args:
        ast: The AST to transform
        elements: List of element types to add IDs to
        prefix: Prefix for generated IDs
        overwrite: Whether to overwrite existing IDs

    Returns:
        Transformed AST
    """
    transformer = IDGeneratorTransformer(
        {
            "prefix": prefix,
            "overwrite": overwrite,
            "target_elements": elements,
        }
    )
    return transformer.transform(ast)
