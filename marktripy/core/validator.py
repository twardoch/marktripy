# this_file: marktripy/core/validator.py
"""AST validation utilities for marktripy."""

from __future__ import annotations

from loguru import logger

from marktripy.core.ast import (
    ASTNode,
    BlockQuote,
    Document,
    Heading,
    Image,
    Link,
    List,
    ListItem,
    Table,
    TableCell,
    TableRow,
)


class ValidationError(Exception):
    """Raised when AST validation fails."""

    def __init__(self, message: str, node: ASTNode | None = None):
        """Initialize validation error.

        Args:
            message: Error description
            node: The node that failed validation
        """
        self.node = node
        if node:
            super().__init__(f"{message} at {node.type} node")
        else:
            super().__init__(message)


class ASTValidator:
    """Validates AST structure and content."""

    def __init__(self, strict: bool = False):
        """Initialize validator.

        Args:
            strict: Whether to enforce strict validation rules
        """
        self.strict = strict
        self.errors: list[ValidationError] = []
        logger.debug(f"Initialized ASTValidator with strict={strict}")

    def validate(self, ast: Document) -> list[ValidationError]:
        """Validate an entire AST.

        Args:
            ast: The AST to validate

        Returns:
            List of validation errors (empty if valid)
        """
        self.errors = []
        self._validate_node(ast)
        logger.info(f"Validation complete: {len(self.errors)} errors found")
        return self.errors

    def validate_strict(self, ast: Document) -> None:
        """Validate an AST and raise on first error.

        Args:
            ast: The AST to validate

        Raises:
            ValidationError: If validation fails
        """
        errors = self.validate(ast)
        if errors:
            raise errors[0]

    def _validate_node(self, node: ASTNode) -> None:
        """Validate a single node and its children.

        Args:
            node: The node to validate
        """
        # Validate node structure
        if not node.type:
            self._add_error("Node has no type", node)
            return

        # Type-specific validation
        method_name = f"_validate_{node.type}"
        validator = getattr(self, method_name, self._validate_generic)
        validator(node)

        # Validate children
        for child in node.children:
            self._validate_node(child)

    def _add_error(self, message: str, node: ASTNode) -> None:
        """Add a validation error.

        Args:
            message: Error message
            node: The node with the error
        """
        error = ValidationError(message, node)
        self.errors.append(error)
        logger.warning(f"Validation error: {error}")

    def _validate_generic(self, node: ASTNode) -> None:
        """Generic validation for unknown node types.

        Args:
            node: The node to validate
        """
        if self.strict:
            logger.warning(f"Unknown node type in strict mode: {node.type}")

    def _validate_document(self, node: Document) -> None:
        """Validate document node.

        Args:
            node: Document node to validate
        """
        # Document should only contain block-level elements
        for child in node.children:
            if child.type in ["text", "emphasis", "strong", "inline_code"]:
                self._add_error("Document contains inline element", child)

    def _validate_heading(self, node: Heading) -> None:
        """Validate heading node.

        Args:
            node: Heading node to validate
        """
        if not 1 <= node.level <= 6:
            self._add_error(f"Invalid heading level: {node.level}", node)

        # Headings should contain inline elements
        if not node.children and not node.content:
            self._add_error("Heading has no content", node)

    def _validate_list(self, node: List) -> None:
        """Validate list node.

        Args:
            node: List node to validate
        """
        # Lists should only contain list items
        for child in node.children:
            if child.type != "list_item":
                self._add_error(f"List contains non-list-item: {child.type}", child)

        if node.ordered and node.start is not None and node.start < 0:
            self._add_error(f"Invalid list start: {node.start}", node)

    def _validate_list_item(self, node: ListItem) -> None:
        """Validate list item node.

        Args:
            node: List item node to validate
        """
        # List items should have content
        if not node.children and not node.content and self.strict:
            self._add_error("Empty list item", node)

    def _validate_link(self, node: Link) -> None:
        """Validate link node.

        Args:
            node: Link node to validate
        """
        if not node.href:
            self._add_error("Link has no href", node)

        # Links should have content
        if not node.children and not node.content and self.strict:
            self._add_error("Link has no text", node)

    def _validate_image(self, node: Image) -> None:
        """Validate image node.

        Args:
            node: Image node to validate
        """
        if not node.src:
            self._add_error("Image has no src", node)

        # Images should not have children
        if node.children:
            self._add_error("Image has children", node)

    def _validate_table(self, node: Table) -> None:
        """Validate table node.

        Args:
            node: Table node to validate
        """
        # Tables should only contain table rows
        for child in node.children:
            if child.type != "table_row":
                self._add_error(f"Table contains non-row: {child.type}", child)

        # Validate table structure
        if node.children:
            row_lengths = [len(row.children) for row in node.children if isinstance(row, TableRow)]
            if row_lengths and len(set(row_lengths)) > 1:
                self._add_error("Table has inconsistent column counts", node)

    def _validate_table_row(self, node: TableRow) -> None:
        """Validate table row node.

        Args:
            node: Table row node to validate
        """
        # Rows should only contain table cells
        for child in node.children:
            if child.type != "table_cell":
                self._add_error(f"Table row contains non-cell: {child.type}", child)

    def _validate_table_cell(self, node: TableCell) -> None:
        """Validate table cell node.

        Args:
            node: Table cell node to validate
        """
        # Cells can contain any content
        pass

    def _validate_blockquote(self, node: BlockQuote) -> None:
        """Validate blockquote node.

        Args:
            node: Blockquote node to validate
        """
        # Blockquotes should have content
        if not node.children and self.strict:
            self._add_error("Empty blockquote", node)


def validate_ast(ast: Document, strict: bool = False) -> list[ValidationError]:
    """Convenience function to validate an AST.

    Args:
        ast: The AST to validate
        strict: Whether to enforce strict validation

    Returns:
        List of validation errors
    """
    validator = ASTValidator(strict=strict)
    return validator.validate(ast)


def validate_ast_strict(ast: Document) -> None:
    """Validate an AST and raise on error.

    Args:
        ast: The AST to validate

    Raises:
        ValidationError: If validation fails
    """
    validator = ASTValidator(strict=True)
    validator.validate_strict(ast)
