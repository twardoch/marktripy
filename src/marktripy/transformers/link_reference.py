# this_file: marktripy/transformers/link_reference.py
"""Link reference transformer for marktripy."""

from __future__ import annotations

from typing import Any

from loguru import logger

from marktripy.core.ast import Document, Link, Paragraph, Text
from marktripy.transformers.base import Transformer


class LinkReferenceTransformer(Transformer):
    """Transforms inline links to reference-style links.

    Collects all links and creates a reference section at the
    end of the document.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize link reference transformer.

        Args:
            config: Transformer configuration with options:
                - style: 'numeric' or 'text' (default: 'numeric')
                - section_title: Title for references section (default: 'References')
                - dedup: Whether to deduplicate same URLs (default: True)
                - preserve_titles: Whether to preserve link titles (default: True)
        """
        super().__init__(config)

        self.style = self.config.get("style", "numeric")
        self.section_title = self.config.get("section_title", "References")
        self.dedup = self.config.get("dedup", True)
        self.preserve_titles = self.config.get("preserve_titles", True)

        # Track links and references
        self.links: list[tuple[str, str, str | None]] = []  # (text, href, title)
        self.references: dict[str, str] = {}  # href -> reference_id
        self.reference_counter = 0

    def get_description(self) -> str:
        """Get transformer description.

        Returns:
            Description of what this transformer does
        """
        return f"Converts inline links to {self.style} reference-style links"

    def transform(self, ast: Document) -> Document:
        """Transform inline links to reference links.

        Args:
            ast: The AST to transform

        Returns:
            Transformed AST
        """
        # Reset state
        self.links = []
        self.references = {}
        self.reference_counter = 0

        # First pass: collect and transform links
        result = super().transform(ast)

        # Second pass: add reference section if we found links
        if self.links:
            self._add_reference_section(result)

        return result

    def visit_link(self, node: Link) -> Link:
        """Transform an inline link to reference style.

        Args:
            node: The link to transform

        Returns:
            Transformed link
        """
        # Visit children first
        self.generic_visit(node)

        # Skip if already a reference-style link
        if not node.href:
            return node

        # Get link text
        link_text = self._get_link_text(node)

        # Generate or get reference ID
        if self.dedup and node.href in self.references:
            ref_id = self.references[node.href]
        else:
            ref_id = self._generate_reference_id(link_text, node.href)
            self.references[node.href] = ref_id

        # Store link info
        title = node.title if self.preserve_titles else None
        self.links.append((ref_id, node.href, title))

        # Transform the link
        logger.debug(f"Converting link '{link_text}' to reference [{ref_id}]")

        # Create reference-style link
        # For now, we'll store the reference ID in a custom attribute
        node.set_attr("reference_id", ref_id)

        return node

    def _get_link_text(self, node: Link) -> str:
        """Extract text content from a link node.

        Args:
            node: Link node

        Returns:
            Link text
        """
        from marktripy.utils.slugify import extract_text

        return extract_text(node)

    def _generate_reference_id(self, text: str, href: str) -> str:
        """Generate a reference ID for a link.

        Args:
            text: Link text
            href: Link URL

        Returns:
            Reference ID
        """
        if self.style == "numeric":
            self.reference_counter += 1
            return str(self.reference_counter)
        # text style
        # Use slugified text as base
        from marktripy.utils.slugify import slugify

        base_id = slugify(text, lowercase=True, max_length=50)
        if not base_id:
            base_id = "link"

        # Make unique if needed
        if base_id not in [ref_id for ref_id, _, _ in self.links]:
            return base_id

        # Add counter to make unique
        counter = 1
        while f"{base_id}-{counter}" in [ref_id for ref_id, _, _ in self.links]:
            counter += 1

        return f"{base_id}-{counter}"

    def _add_reference_section(self, ast: Document) -> None:
        """Add a reference section to the document.

        Args:
            ast: The document to add references to
        """
        from marktripy.core.ast import Heading

        # Create heading for references
        if self.section_title:
            heading = Heading(level=2)
            heading.add_child(Text(content=self.section_title))
            ast.add_child(heading)

        # Add references
        seen_refs = set()
        for ref_id, href, title in self.links:
            # Skip duplicates if deduping
            if self.dedup and href in seen_refs:
                continue
            seen_refs.add(href)

            # Create reference paragraph
            para = Paragraph()
            ref_text = f"[{ref_id}]: {href}"
            if title:
                ref_text += f' "{title}"'
            para.add_child(Text(content=ref_text))
            ast.add_child(para)

        logger.info(f"Added {len(seen_refs)} references to document")


class LinkCollector(Transformer):
    """Collects all links in a document without transforming them."""

    def __init__(self):
        """Initialize link collector."""
        super().__init__()
        self.links: list[Link] = []

    def get_description(self) -> str:
        """Get transformer description.

        Returns:
            Description of what this transformer does
        """
        return "Collects all links in the document"

    def visit_link(self, node: Link) -> Link:
        """Collect a link node.

        Args:
            node: The link to collect

        Returns:
            The unchanged link
        """
        self.links.append(node)
        self.generic_visit(node)
        return node

    def get_links(self) -> list[Link]:
        """Get collected links.

        Returns:
            List of link nodes
        """
        return self.links


# Convenience functions
def convert_to_reference_links(
    ast: Document, style: str = "numeric", dedup: bool = True
) -> Document:
    """Convert all inline links to reference-style links.

    Args:
        ast: The AST to transform
        style: Reference style ('numeric' or 'text')
        dedup: Whether to deduplicate same URLs

    Returns:
        Transformed AST
    """
    transformer = LinkReferenceTransformer({"style": style, "dedup": dedup})
    return transformer.transform(ast)


def collect_links(ast: Document) -> list[Link]:
    """Collect all links in the document.

    Args:
        ast: The document to search

    Returns:
        List of link nodes
    """
    collector = LinkCollector()
    collector.transform(ast)
    return collector.get_links()
