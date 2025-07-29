# this_file: marktripy/transformers/toc.py
"""Table of contents generator for marktripy."""

from __future__ import annotations

from typing import Any

from loguru import logger

from marktripy.core.ast import ASTNode, Document, Heading, Link, List, ListItem, Paragraph, Text
from marktripy.transformers.base import Transformer
from marktripy.utils.slugify import extract_text


class TOCGenerator(Transformer):
    """Generates a table of contents from document headings.

    Can insert the TOC at a specific location or return it separately.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize TOC generator.

        Args:
            config: Transformer configuration with options:
                - min_level: Minimum heading level to include (default: 1)
                - max_level: Maximum heading level to include (default: 3)
                - title: TOC title (default: 'Table of Contents')
                - marker: Marker text to replace with TOC (default: '[[TOC]]')
                - insert: Whether to insert TOC in document (default: True)
                - ordered: Whether to use ordered list (default: False)
                - indent_size: Spaces per indent level (default: 2)
        """
        super().__init__(config)

        self.min_level = self.config.get("min_level", 1)
        self.max_level = self.config.get("max_level", 3)
        self.title = self.config.get("title", "Table of Contents")
        self.marker = self.config.get("marker", "[[TOC]]")
        self.insert = self.config.get("insert", True)
        self.ordered = self.config.get("ordered", False)
        self.indent_size = self.config.get("indent_size", 2)

        # Collected headings
        self.headings: list[tuple[int, str, str | None]] = []  # (level, text, id)
        self.toc_node: ASTNode | None = None

    def get_description(self) -> str:
        """Get transformer description.

        Returns:
            Description of what this transformer does
        """
        return (
            f"Generates table of contents from headings (levels {self.min_level}-{self.max_level})"
        )

    def transform(self, ast: Document) -> Document:
        """Generate and optionally insert TOC.

        Args:
            ast: The AST to process

        Returns:
            Document with TOC inserted (if configured)
        """
        # Reset state
        self.headings = []
        self.toc_node = None

        # Collect headings
        self._collect_headings(ast)

        # Generate TOC
        if self.headings:
            self.toc_node = self._generate_toc()

        # Insert TOC if requested
        return self._insert_toc(ast) if self.insert and self.toc_node else ast

    def get_toc(self) -> ASTNode | None:
        """Get the generated TOC node.

        Returns:
            The TOC node, or None if no headings found
        """
        return self.toc_node

    def _collect_headings(self, node: ASTNode) -> None:
        """Collect all headings in the specified level range.

        Args:
            node: Node to search for headings
        """
        if isinstance(node, Heading) and self.min_level <= node.level <= self.max_level:
            text = extract_text(node)
            heading_id = node.get_attr("id")
            self.headings.append((node.level, text, heading_id))
            logger.debug(f"Found heading: L{node.level} '{text}' (id: {heading_id})")

        # Recurse into children
        for child in node.children:
            self._collect_headings(child)

    def _generate_toc(self) -> ASTNode:
        """Generate the TOC structure.

        Returns:
            Root node of the TOC
        """
        from marktripy.core.ast import Document

        # Create container
        toc_container = Document()

        # Add title if specified
        if self.title:
            title_heading = Heading(level=2)
            title_heading.add_child(Text(content=self.title))
            toc_container.add_child(title_heading)

        # Create nested list structure
        root_list = self._create_toc_list(self.headings)
        if root_list:
            toc_container.add_child(root_list)

        logger.info(f"Generated TOC with {len(self.headings)} entries")
        return toc_container

    def _create_toc_list(self, headings: list[tuple[int, str, str | None]]) -> List | None:
        """Create nested list structure for TOC.

        Args:
            headings: List of (level, text, id) tuples

        Returns:
            Root list node, or None if no headings
        """
        if not headings:
            return None

        # Normalize levels to start from 0
        min_level = min(h[0] for h in headings)
        normalized = [(level - min_level, text, heading_id) for level, text, heading_id in headings]

        # Build tree structure
        root = List(ordered=self.ordered)
        stack: list[tuple[List, int]] = [(root, -1)]

        for level, text, heading_id in normalized:
            # Pop stack until we find parent level
            while stack and stack[-1][1] >= level:
                stack.pop()

            # Create list item
            item = ListItem()

            # Create link if heading has ID
            if heading_id:
                link = Link(href=f"#{heading_id}")
                link.add_child(Text(content=text))
                item.add_child(link)
            else:
                item.add_child(Text(content=text))

            # Add to current list
            current_list = stack[-1][0]
            current_list.add_child(item)

            # Create nested list if needed for next item
            if level > stack[-1][1]:
                nested_list = List(ordered=self.ordered)
                item.add_child(nested_list)
                stack.append((nested_list, level))

        return root

    def _insert_toc(self, ast: Document) -> Document:
        """Insert TOC into the document.

        Args:
            ast: Document to insert TOC into

        Returns:
            Document with TOC inserted
        """
        # Clone the AST to avoid modifying the original
        result = ast.clone()

        # Find marker or insert at beginning
        marker_found = self._replace_marker(result)

        if not marker_found:
            # Insert at beginning after any front matter
            insert_pos = self._find_insert_position(result)
            for i, child in enumerate(self.toc_node.children):
                result.children.insert(insert_pos + i, child)
            logger.info(f"Inserted TOC at position {insert_pos}")

        return result

    def _replace_marker(self, node: ASTNode) -> bool:
        """Replace TOC marker with actual TOC.

        Args:
            node: Node to search for marker

        Returns:
            True if marker was found and replaced
        """
        # Check if this is a paragraph with just the marker
        if isinstance(node, Paragraph) and len(node.children) == 1:
            child = node.children[0]
            if isinstance(child, Text) and child.content and child.content.strip() == self.marker:
                # Replace this paragraph with TOC
                parent = self._find_parent(node.walk()[0], node)
                if parent:
                    index = parent.children.index(node)
                    parent.children.pop(index)
                    for i, toc_child in enumerate(self.toc_node.children):
                        parent.children.insert(index + i, toc_child)
                    logger.info(f"Replaced marker '{self.marker}' with TOC")
                    return True

        # Recurse into children
        return any(self._replace_marker(child) for child in node.children)

    def _find_parent(self, root: ASTNode, target: ASTNode) -> ASTNode | None:
        """Find parent of a node.

        Args:
            root: Root node to search from
            target: Node to find parent of

        Returns:
            Parent node, or None if not found
        """
        for node in root.walk():
            if target in node.children:
                return node
        return None

    def _find_insert_position(self, doc: Document) -> int:
        """Find appropriate position to insert TOC.

        Args:
            doc: Document to analyze

        Returns:
            Index to insert TOC at
        """
        # Skip any front matter or title heading
        for i, child in enumerate(doc.children):
            # Skip metadata or front matter paragraphs
            if isinstance(child, Paragraph):
                text = extract_text(child).strip()
                if text.startswith("---") or text.startswith("+++"):
                    continue

            # Skip first heading if it's level 1 (likely title)
            if isinstance(child, Heading) and child.level == 1:
                return i + 1

            # Otherwise insert here
            return i

        # Insert at end if nothing found
        return len(doc.children)


# Convenience functions
def generate_toc(ast: Document, max_level: int = 3, insert: bool = True) -> Document:
    """Generate table of contents for the document.

    Args:
        ast: The document to process
        max_level: Maximum heading level to include
        insert: Whether to insert TOC in document

    Returns:
        Document with TOC (if insert=True), otherwise original document
    """
    generator = TOCGenerator({"max_level": max_level, "insert": insert})
    return generator.transform(ast)


def extract_toc(ast: Document, max_level: int = 3) -> ASTNode | None:
    """Extract table of contents without modifying document.

    Args:
        ast: The document to analyze
        max_level: Maximum heading level to include

    Returns:
        TOC node, or None if no headings found
    """
    generator = TOCGenerator({"max_level": max_level, "insert": False})
    generator.transform(ast)
    return generator.get_toc()
