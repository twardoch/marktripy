# this_file: marktripy/transformers/heading.py
"""Heading level transformer for marktripy."""

from __future__ import annotations

from typing import Any

from loguru import logger

from marktripy.core.ast import ASTNode, Document, Heading
from marktripy.transformers.base import Transformer


class HeadingLevelTransformer(Transformer):
    """Transforms heading levels in an AST.

    Can increase/decrease all heading levels, set absolute levels,
    or normalize heading hierarchy.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize heading transformer.

        Args:
            config: Transformer configuration with options:
                - operation: 'increase', 'decrease', 'set', or 'normalize'
                - amount: How much to change levels (for increase/decrease)
                - level: Target level (for set operation)
                - min_level: Minimum allowed level (default: 1)
                - max_level: Maximum allowed level (default: 6)
        """
        super().__init__(config)

        self.operation = self.config.get("operation", "increase")
        self.amount = self.config.get("amount", 1)
        self.level = self.config.get("level", 1)
        self.min_level = self.config.get("min_level", 1)
        self.max_level = self.config.get("max_level", 6)

        # Track original levels for normalization
        self.original_levels: list[int] = []

    def get_description(self) -> str:
        """Get transformer description.

        Returns:
            Description of what this transformer does
        """
        if self.operation == "increase":
            return f"Increases heading levels by {self.amount}"
        if self.operation == "decrease":
            return f"Decreases heading levels by {self.amount}"
        if self.operation == "set":
            return f"Sets all headings to level {self.level}"
        if self.operation == "normalize":
            return "Normalizes heading hierarchy starting from level 1"
        return "Unknown heading transformation"

    def transform(self, ast: Document) -> Document:
        """Transform heading levels in the AST.

        Args:
            ast: The AST to transform

        Returns:
            Transformed AST
        """
        # For normalization, first collect all heading levels
        if self.operation == "normalize":
            self.original_levels = []
            self._collect_heading_levels(ast)
            logger.debug(f"Found heading levels: {sorted(set(self.original_levels))}")

        # Apply transformation
        return super().transform(ast)

    def visit_heading(self, node: Heading) -> Heading:
        """Transform a heading node.

        Args:
            node: The heading to transform

        Returns:
            Transformed heading
        """
        new_level = self._calculate_new_level(node.level)

        if new_level != node.level:
            logger.debug(f"Changing heading level from {node.level} to {new_level}")
            node.level = new_level

        # Visit children
        self.generic_visit(node)
        return node

    def _calculate_new_level(self, current_level: int) -> int:
        """Calculate new heading level based on operation.

        Args:
            current_level: Current heading level

        Returns:
            New heading level
        """
        if self.operation == "increase":
            new_level = current_level + self.amount
        elif self.operation == "decrease":
            new_level = current_level - self.amount
        elif self.operation == "set":
            new_level = self.level
        elif self.operation == "normalize":
            new_level = self._normalize_level(current_level)
        else:
            logger.warning(f"Unknown operation: {self.operation}")
            new_level = current_level

        # Clamp to valid range
        return max(self.min_level, min(new_level, self.max_level))

    def _normalize_level(self, current_level: int) -> int:
        """Normalize heading level to maintain hierarchy.

        Args:
            current_level: Current heading level

        Returns:
            Normalized level
        """
        if not self.original_levels:
            return current_level

        # Find unique levels and sort them
        unique_levels = sorted(set(self.original_levels))

        # Map original levels to normalized levels (1, 2, 3, ...)
        level_map = {old: new + 1 for new, old in enumerate(unique_levels)}

        return level_map.get(current_level, current_level)

    def _collect_heading_levels(self, node: ASTNode) -> None:
        """Collect all heading levels in the AST.

        Args:
            node: Node to search for headings
        """
        if isinstance(node, Heading):
            self.original_levels.append(node.level)

        for child in node.children:
            self._collect_heading_levels(child)


class HeadingShifter(HeadingLevelTransformer):
    """Convenience class for shifting heading levels up or down."""

    def __init__(self, shift: int):
        """Initialize heading shifter.

        Args:
            shift: Amount to shift (positive = increase, negative = decrease)
        """
        if shift > 0:
            config = {"operation": "increase", "amount": shift}
        else:
            config = {"operation": "decrease", "amount": abs(shift)}

        super().__init__(config)


class HeadingNormalizer(HeadingLevelTransformer):
    """Convenience class for normalizing heading hierarchy."""

    def __init__(self):
        """Initialize heading normalizer."""
        super().__init__({"operation": "normalize"})


# Convenience functions
def increase_heading_levels(ast: Document, amount: int = 1) -> Document:
    """Increase all heading levels.

    Args:
        ast: The AST to transform
        amount: How much to increase levels

    Returns:
        Transformed AST
    """
    transformer = HeadingLevelTransformer({"operation": "increase", "amount": amount})
    return transformer.transform(ast)


def decrease_heading_levels(ast: Document, amount: int = 1) -> Document:
    """Decrease all heading levels.

    Args:
        ast: The AST to transform
        amount: How much to decrease levels

    Returns:
        Transformed AST
    """
    transformer = HeadingLevelTransformer({"operation": "decrease", "amount": amount})
    return transformer.transform(ast)


def normalize_headings(ast: Document) -> Document:
    """Normalize heading hierarchy to start from level 1.

    Args:
        ast: The AST to transform

    Returns:
        Transformed AST
    """
    transformer = HeadingNormalizer()
    return transformer.transform(ast)
