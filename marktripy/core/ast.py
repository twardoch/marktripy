# this_file: marktripy/core/ast.py
"""Abstract Syntax Tree node definitions for marktripy."""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import Any

from loguru import logger


@dataclass
class ASTNode(ABC):
    """Base class for all AST nodes.

    This represents a node in the Markdown abstract syntax tree. Each node
    has a type, optional children, attributes, content, and metadata.

    Attributes:
        type: The type of node (e.g., 'heading', 'paragraph', 'list')
        children: List of child nodes
        attrs: Dictionary of attributes (e.g., 'id', 'class')
        content: Optional text content for leaf nodes
        meta: Parser-specific metadata (e.g., source position)
    """

    type: str
    children: list[ASTNode] = field(default_factory=list)
    attrs: dict[str, Any] = field(default_factory=dict)
    content: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate node after initialization."""
        if not self.type:
            raise ValueError("Node type cannot be empty")
        logger.debug(f"Created ASTNode: type={self.type}, children={len(self.children)}")

    def add_child(self, child: ASTNode) -> None:
        """Add a child node."""
        self.children.append(child)
        logger.debug(f"Added child {child.type} to {self.type}")

    def remove_child(self, child: ASTNode) -> None:
        """Remove a child node."""
        self.children.remove(child)
        logger.debug(f"Removed child {child.type} from {self.type}")

    def get_attr(self, name: str, default: Any = None) -> Any:
        """Get an attribute value."""
        return self.attrs.get(name, default)

    def set_attr(self, name: str, value: Any) -> None:
        """Set an attribute value."""
        self.attrs[name] = value
        logger.debug(f"Set attribute {name}={value} on {self.type}")

    def walk(self) -> list[ASTNode]:
        """Walk the tree and return all nodes in depth-first order."""
        nodes = [self]
        for child in self.children:
            nodes.extend(child.walk())
        return nodes

    def find_all(self, node_type: str) -> list[ASTNode]:
        """Find all nodes of a specific type in the subtree."""
        return [node for node in self.walk() if node.type == node_type]

    def replace_child(self, old_child: ASTNode, new_child: ASTNode) -> None:
        """Replace a child node with another."""
        try:
            index = self.children.index(old_child)
            self.children[index] = new_child
            logger.debug(f"Replaced child {old_child.type} with {new_child.type}")
        except ValueError as e:
            raise ValueError(f"Child {old_child.type} not found in {self.type}") from e

    def clone(self) -> ASTNode:
        """Create a deep copy of this node and its subtree."""
        import copy

        # Create a shallow copy of the node
        cloned = copy.copy(self)
        # Deep copy the mutable attributes
        cloned.children = [child.clone() for child in self.children]
        cloned.attrs = self.attrs.copy()
        cloned.meta = self.meta.copy()
        return cloned


# Concrete node types
@dataclass
class Document(ASTNode):
    """Root document node."""

    def __init__(self, **kwargs):
        super().__init__(type="document", **kwargs)


@dataclass
class Heading(ASTNode):
    """Heading node with level."""

    level: int = 1

    def __init__(self, level: int = 1, **kwargs):
        super().__init__(type="heading", **kwargs)
        self.level = level
        if not 1 <= level <= 6:
            raise ValueError(f"Heading level must be 1-6, got {level}")


@dataclass
class Paragraph(ASTNode):
    """Paragraph node."""

    def __init__(self, **kwargs):
        super().__init__(type="paragraph", **kwargs)


@dataclass
class Text(ASTNode):
    """Text leaf node."""

    def __init__(self, content: str, **kwargs):
        super().__init__(type="text", content=content, **kwargs)


@dataclass
class Emphasis(ASTNode):
    """Emphasis (italic) node."""

    def __init__(self, **kwargs):
        super().__init__(type="emphasis", **kwargs)


@dataclass
class Strong(ASTNode):
    """Strong (bold) node."""

    def __init__(self, **kwargs):
        super().__init__(type="strong", **kwargs)


@dataclass
class Link(ASTNode):
    """Link node with href and title."""

    href: str = ""
    title: str | None = None

    def __init__(self, href: str = "", title: str | None = None, **kwargs):
        super().__init__(type="link", **kwargs)
        self.href = href
        self.title = title
        self.set_attr("href", href)
        if title:
            self.set_attr("title", title)


@dataclass
class Image(ASTNode):
    """Image node with src, alt, and title."""

    src: str = ""
    alt: str = ""
    title: str | None = None

    def __init__(self, src: str = "", alt: str = "", title: str | None = None, **kwargs):
        super().__init__(type="image", **kwargs)
        self.src = src
        self.alt = alt
        self.title = title
        self.set_attr("src", src)
        self.set_attr("alt", alt)
        if title:
            self.set_attr("title", title)


@dataclass
class CodeBlock(ASTNode):
    """Code block with optional language."""

    language: str | None = None

    def __init__(self, content: str, language: str | None = None, **kwargs):
        super().__init__(type="code_block", content=content, **kwargs)
        self.language = language
        if language:
            self.set_attr("language", language)


@dataclass
class InlineCode(ASTNode):
    """Inline code node."""

    def __init__(self, content: str, **kwargs):
        super().__init__(type="inline_code", content=content, **kwargs)


@dataclass
class List(ASTNode):
    """List node (ordered or unordered)."""

    ordered: bool = False
    start: int | None = None
    tight: bool = True

    def __init__(
        self, ordered: bool = False, start: int | None = None, tight: bool = True, **kwargs
    ):
        super().__init__(type="list", **kwargs)
        self.ordered = ordered
        self.start = start
        self.tight = tight
        # Don't set ordered as an HTML attribute - it's determined by tag type
        if start is not None and start != 1:
            self.set_attr("start", start)


@dataclass
class ListItem(ASTNode):
    """List item node."""

    def __init__(self, **kwargs):
        super().__init__(type="list_item", **kwargs)


@dataclass
class BlockQuote(ASTNode):
    """Block quote node."""

    def __init__(self, **kwargs):
        super().__init__(type="blockquote", **kwargs)


@dataclass
class HorizontalRule(ASTNode):
    """Horizontal rule node."""

    def __init__(self, **kwargs):
        super().__init__(type="horizontal_rule", **kwargs)


@dataclass
class Table(ASTNode):
    """Table node."""

    def __init__(self, **kwargs):
        super().__init__(type="table", **kwargs)


@dataclass
class TableRow(ASTNode):
    """Table row node."""

    def __init__(self, **kwargs):
        super().__init__(type="table_row", **kwargs)


@dataclass
class TableCell(ASTNode):
    """Table cell node."""

    header: bool = False
    align: str | None = None

    def __init__(self, header: bool = False, align: str | None = None, **kwargs):
        super().__init__(type="table_cell", **kwargs)
        self.header = header
        self.align = align
        if align:
            self.set_attr("align", align)
