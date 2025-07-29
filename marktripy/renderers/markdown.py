# this_file: marktripy/renderers/markdown.py
"""Markdown renderer for marktripy."""

from __future__ import annotations

from typing import Any

from loguru import logger

from marktripy.core.ast import (
    ASTNode,
    BlockQuote,
    CodeBlock,
    Document,
    Emphasis,
    Heading,
    HorizontalRule,
    Image,
    InlineCode,
    Link,
    List,
    ListItem,
    Paragraph,
    Strong,
    Table,
    TableCell,
    TableRow,
    Text,
)
from marktripy.renderers.base import RenderContext, Renderer, RendererRegistry


class MarkdownRenderer(Renderer):
    """Renderer that converts AST back to Markdown."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize Markdown renderer.

        Args:
            config: Renderer configuration with options:
                - preserve_format: Try to preserve original formatting
                - heading_style: 'atx' (default) or 'setext' for h1/h2
                - emphasis_char: Character for emphasis ('*' or '_')
                - strong_char: Character for strong ('**' or '__')
                - bullet_char: Character for bullets ('-', '*', or '+')
                - code_fence: Fence character for code blocks ('`' or '~')
                - line_width: Maximum line width (0 = no wrap)
        """
        super().__init__(config)

        self.preserve_format = self.config.get("preserve_format", False)
        self.heading_style = self.config.get("heading_style", "atx")
        self.emphasis_char = self.config.get("emphasis_char", "*")
        self.strong_char = self.config.get("strong_char", "**")
        self.bullet_char = self.config.get("bullet_char", "-")
        self.code_fence = self.config.get("code_fence", "`")
        self.line_width = self.config.get("line_width", 0)

        self.context = RenderContext()
        logger.info("Initialized MarkdownRenderer")

    def render(self, ast: Document) -> str:
        """Render an AST to Markdown.

        Args:
            ast: The AST to render

        Returns:
            The rendered Markdown
        """
        self.context = RenderContext()
        return self.render_node(ast).rstrip() + "\n"

    def render_node(self, node: ASTNode) -> str:
        """Render a single AST node.

        Args:
            node: The node to render

        Returns:
            The rendered Markdown
        """
        method_name = f"render_{node.type}"
        render_method = getattr(self, method_name, self.render_unknown)
        return render_method(node)

    def render_unknown(self, node: ASTNode) -> str:
        """Render unknown node types.

        Args:
            node: The unknown node

        Returns:
            Empty string with warning
        """
        logger.warning(f"Unknown node type: {node.type}")
        return ""

    def render_children(self, node: ASTNode, separator: str = "") -> str:
        """Render all children of a node.

        Args:
            node: Parent node
            separator: String to join children with

        Returns:
            Concatenated rendered children
        """
        parts = []
        for child in node.children:
            rendered = self.render_node(child)
            if rendered:
                parts.append(rendered)
        return separator.join(parts)

    # Document and structure nodes

    def render_document(self, node: Document) -> str:
        """Render document node."""
        # Render children with double newline between blocks
        parts = []
        for child in node.children:
            rendered = self.render_node(child).rstrip()
            if rendered:
                parts.append(rendered)
        return "\n\n".join(parts) + "\n"

    def render_heading(self, node: Heading) -> str:
        """Render heading node."""
        content = self.render_children(node)

        # Use setext style for h1/h2 if configured
        if self.heading_style == "setext" and node.level <= 2:
            underline = "=" if node.level == 1 else "-"
            return f"{content}\n{underline * len(content)}"

        # Default to ATX style
        return f"{'#' * node.level} {content}"

    def render_paragraph(self, node: Paragraph) -> str:
        """Render paragraph node."""
        content = self.render_children(node)

        # Wrap if configured
        if self.line_width > 0:
            content = self._wrap_text(content, self.line_width)

        return content

    def render_blockquote(self, node: BlockQuote) -> str:
        """Render blockquote node."""
        # Render children
        content = self.render_children(node, "\n\n")

        # Add > prefix to each line
        lines = content.split("\n")
        quoted_lines = [f"> {line}" if line else ">" for line in lines]

        return "\n".join(quoted_lines)

    def render_horizontal_rule(self, node: HorizontalRule) -> str:
        """Render horizontal rule node."""
        return "---"

    # Text nodes

    def render_text(self, node: Text) -> str:
        """Render text node."""
        # Escape special Markdown characters
        text = node.content or ""

        # Escape backslashes first
        text = text.replace("\\", "\\\\")

        # Escape other special characters that need escaping
        # Don't escape period unless it's at the start of a line after a number
        for char in ["*", "_", "`", "[", "]", "(", ")", "#", "+", "-", "!", "|", "{", "}"]:
            text = text.replace(char, f"\\{char}")

        return text

    def render_emphasis(self, node: Emphasis) -> str:
        """Render emphasis (italic) node."""
        content = self.render_children(node)
        return f"{self.emphasis_char}{content}{self.emphasis_char}"

    def render_strong(self, node: Strong) -> str:
        """Render strong (bold) node."""
        content = self.render_children(node)
        return f"{self.strong_char}{content}{self.strong_char}"

    # Code nodes

    def render_code_block(self, node: CodeBlock) -> str:
        """Render code block node."""
        content = node.content or ""
        language = node.language or ""

        # Use fence style
        fence = self.code_fence * 3

        # Ensure content doesn't contain fence
        if fence in content:
            fence = self.code_fence * 4

        # Remove trailing newline from content if present
        if content.endswith("\n"):
            content = content[:-1]

        return f"{fence}{language}\n{content}\n{fence}"

    def render_inline_code(self, node: InlineCode) -> str:
        """Render inline code node."""
        content = node.content or ""

        # Determine number of backticks needed
        backticks = "`"
        while backticks in content:
            backticks += "`"

        # Add spaces if content starts/ends with backtick
        if content.startswith("`") or content.endswith("`"):
            return f"{backticks} {content} {backticks}"

        return f"{backticks}{content}{backticks}"

    # Link and image nodes

    def render_link(self, node: Link) -> str:
        """Render link node."""
        text = self.render_children(node)
        href = node.href or ""
        title = node.title

        # Check for reference-style link
        ref_id = node.get_attr("reference_id")
        if ref_id:
            return f"[{text}][{ref_id}]"

        # Inline link
        if title:
            return f'[{text}]({href} "{title}")'
        return f"[{text}]({href})"

    def render_image(self, node: Image) -> str:
        """Render image node."""
        alt = node.alt or ""
        src = node.src or ""
        title = node.title

        if title:
            return f'![{alt}]({src} "{title}")'
        return f"![{alt}]({src})"

    # List nodes

    def render_list(self, node: List) -> str:
        """Render list node."""
        self.context.enter_list(node.tight)

        parts = []
        for i, child in enumerate(node.children):
            if isinstance(child, ListItem):
                # Determine marker
                if node.ordered:
                    start = node.start or 1
                    marker = f"{start + i}."
                else:
                    marker = self.bullet_char

                # Render item
                item_content = self.render_list_item(child)

                # Format with proper indentation
                lines = item_content.split("\n")
                if lines:
                    parts.append(f"{marker} {lines[0]}")
                    # Indent continuation lines
                    for line in lines[1:]:
                        if line:
                            parts.append(f"   {line}")
                        else:
                            parts.append("")

        self.context.exit_list()

        return "\n".join(parts)

    def render_list_item(self, node: ListItem) -> str:
        """Render list item node."""
        # In tight lists, don't add extra newlines
        separator = "\n" if self.context.tight_list else "\n\n"

        content = self.render_children(node, separator)

        # Strip extra newlines for tight lists
        if self.context.tight_list:
            content = content.strip()

        return content

    # Table nodes

    def render_table(self, node: Table) -> str:
        """Render table node."""
        if not node.children:
            return ""

        self.context.enter_table()

        # Collect all rows
        rows = []
        header_row = None

        for i, child in enumerate(node.children):
            if isinstance(child, TableRow):
                # Check if this is a header row
                if i == 0 and all(
                    isinstance(cell, TableCell) and cell.header for cell in child.children
                ):
                    header_row = child
                else:
                    rows.append(child)

        # Calculate column widths
        all_rows = [header_row] if header_row else []
        all_rows.extend(rows)

        col_widths = self._calculate_column_widths(all_rows)

        # Render table
        parts = []

        # Header
        if header_row:
            parts.append(self._render_table_row(header_row, col_widths))
            parts.append(self._render_separator_row(header_row, col_widths))

        # Body
        for row in rows:
            parts.append(self._render_table_row(row, col_widths))

        self.context.exit_table()

        return "\n".join(parts)

    def _render_table_row(self, row: TableRow, col_widths: list[int]) -> str:
        """Render a table row with proper spacing."""
        cells = []

        for i, child in enumerate(row.children):
            if isinstance(child, TableCell):
                content = self.render_children(child).strip()
                width = col_widths[i] if i < len(col_widths) else 0

                # Pad content
                if child.align == "right":
                    cells.append(content.rjust(width))
                elif child.align == "center":
                    cells.append(content.center(width))
                else:
                    cells.append(content.ljust(width))

        return f"| {' | '.join(cells)} |"

    def _render_separator_row(self, header_row: TableRow, col_widths: list[int]) -> str:
        """Render table separator row."""
        separators = []

        for i, child in enumerate(header_row.children):
            if isinstance(child, TableCell):
                width = col_widths[i] if i < len(col_widths) else 3

                # Create separator with alignment
                if child.align == "right":
                    sep = "-" * (width - 1) + ":"
                elif child.align == "center":
                    sep = ":" + "-" * (width - 2) + ":"
                elif child.align == "left":
                    sep = ":" + "-" * (width - 1)
                else:
                    sep = "-" * width

                separators.append(sep)

        return f"| {' | '.join(separators)} |"

    def _calculate_column_widths(self, rows: list[TableRow]) -> list[int]:
        """Calculate minimum column widths for table."""
        if not rows:
            return []

        # Get number of columns
        num_cols = max(len(row.children) for row in rows)
        widths = [3] * num_cols  # Minimum width of 3

        # Calculate max width for each column
        for row in rows:
            for i, child in enumerate(row.children):
                if isinstance(child, TableCell) and i < num_cols:
                    content = self.render_children(child).strip()
                    widths[i] = max(widths[i], len(content))

        return widths

    # Helper methods

    def _wrap_text(self, text: str, width: int) -> str:
        """Wrap text to specified width.

        Args:
            text: Text to wrap
            width: Maximum line width

        Returns:
            Wrapped text
        """
        if not text or width <= 0:
            return text

        # Simple word wrapping (could be improved)
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word)

            if current_length + word_length + len(current_line) <= width:
                current_line.append(word)
                current_length += word_length
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = word_length

        if current_line:
            lines.append(" ".join(current_line))

        return "\n".join(lines)


# Register the renderer
RendererRegistry.register("markdown", MarkdownRenderer)
