# this_file: marktripy/utils/slugify.py
"""Text slugification utilities for marktripy."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from loguru import logger


def slugify(
    text: str,
    lowercase: bool = True,
    separator: str = "-",
    max_length: int | None = None,
    allowed_chars: str | None = None,
) -> str:
    """Convert text to a URL-friendly slug.

    Args:
        text: Text to slugify
        lowercase: Whether to convert to lowercase
        separator: Character to use as separator
        max_length: Maximum length of the slug
        allowed_chars: Additional allowed characters (besides alphanumeric)

    Returns:
        Slugified text
    """
    if not text:
        return ""

    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")

    # Convert to lowercase if requested
    if lowercase:
        text = text.lower()

    # Build allowed character pattern
    if allowed_chars:
        # Escape special regex characters
        escaped_chars = re.escape(allowed_chars)
        pattern = f"[^a-zA-Z0-9{escaped_chars}\\s-]"
    else:
        pattern = r"[^a-zA-Z0-9\s-]"

    # Remove non-allowed characters
    text = re.sub(pattern, "", text)

    # Replace spaces and multiple hyphens with separator
    text = re.sub(r"[\s-]+", separator, text)

    # Remove separator from start/end
    text = text.strip(separator)

    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length].rstrip(separator)

    logger.debug(f"Slugified text: '{text}'")
    return text


def generate_id(text: str, existing_ids: set[str] | None = None) -> str:
    """Generate a unique ID from text.

    Args:
        text: Text to generate ID from
        existing_ids: Set of existing IDs to avoid duplicates

    Returns:
        Unique ID
    """
    if existing_ids is None:
        existing_ids = set()

    # Generate base ID
    base_id = slugify(text, lowercase=True, separator="-")

    # Handle empty slug
    if not base_id:
        base_id = "section"

    # Make unique if needed
    if base_id not in existing_ids:
        return base_id

    # Add suffix to make unique
    counter = 1
    while f"{base_id}-{counter}" in existing_ids:
        counter += 1

    unique_id = f"{base_id}-{counter}"
    logger.debug(f"Generated unique ID: {unique_id}")
    return unique_id


def extract_text(node: Any) -> str:
    """Extract plain text from an AST node.

    Args:
        node: AST node to extract text from

    Returns:
        Plain text content
    """
    # Import here to avoid circular dependency
    from marktripy.core.ast import ASTNode

    if not isinstance(node, ASTNode):
        return str(node)

    # If node has direct content, use it
    if node.content:
        return node.content

    # Otherwise, concatenate children's text
    text_parts = []
    for child in node.children:
        text_parts.append(extract_text(child))

    return "".join(text_parts)


class IDGenerator:
    """Stateful ID generator that tracks used IDs."""

    def __init__(self, prefix: str = "", separator: str = "-"):
        """Initialize ID generator.

        Args:
            prefix: Optional prefix for all IDs
            separator: Separator character
        """
        self.prefix = prefix
        self.separator = separator
        self.used_ids: set[str] = set()
        logger.debug(f"Initialized IDGenerator with prefix='{prefix}'")

    def generate(self, text: str) -> str:
        """Generate a unique ID from text.

        Args:
            text: Text to generate ID from

        Returns:
            Unique ID
        """
        # Add prefix if specified
        if self.prefix:
            text = f"{self.prefix}{self.separator}{text}"

        # Generate unique ID
        unique_id = generate_id(text, self.used_ids)
        self.used_ids.add(unique_id)

        return unique_id

    def reset(self) -> None:
        """Reset the used IDs set."""
        self.used_ids.clear()
        logger.debug("Reset ID generator")

    def has_id(self, id_value: str) -> bool:
        """Check if an ID has been used.

        Args:
            id_value: ID to check

        Returns:
            True if ID has been used
        """
        return id_value in self.used_ids
