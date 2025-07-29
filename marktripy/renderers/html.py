# this_file: marktripy/renderers/html.py
"""HTML renderer implementation for marktripy."""

from __future__ import annotations

import html
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


class HTMLRenderer(Renderer):
    """Renderer that converts AST to HTML."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize HTML renderer.

        Args:
            config: Renderer configuration with options:
                - xhtml: Use XHTML syntax (self-closing tags)
                - breaks: Convert newlines to <br>
                - langPrefix: Prefix for code block language classes
                - linkify: Auto-convert URLs to links
                - typographer: Enable smart quotes
                - quotes: Quote characters for typographer
        """
        super().__init__(config)

        self.xhtml = self.config.get("xhtml", False)
        self.breaks = self.config.get("breaks", False)
        self.lang_prefix = self.config.get("langPrefix", "language-")
        self.linkify = self.config.get("linkify", False)
        self.typographer = self.config.get("typographer", False)
        self.quotes = self.config.get("quotes", '""' + "''")

        self.context = RenderContext()
        logger.info("Initialized HTMLRenderer")

    def render(self, ast: Document) -> str:
        """Render an AST to HTML.

        Args:
            ast: The AST to render

        Returns:
            The rendered HTML
        """
        self.context = RenderContext()
        return self.render_node(ast)

    def render_node(self, node: ASTNode) -> str:
        """Render a single AST node.

        Args:
            node: The node to render

        Returns:
            The rendered HTML
        """
        method_name = f"render_{node.type}"
        render_method = getattr(self, method_name, self.render_unknown)
        return render_method(node)

    def render_unknown(self, node: ASTNode) -> str:
        """Render unknown node types.

        Args:
            node: The unknown node

        Returns:
            HTML comment with node info
        """
        logger.warning(f"Unknown node type: {node.type}")
        return f"<!-- Unknown node type: {node.type} -->"

    def escape(self, text: str) -> str:
        """Escape text for HTML.

        Args:
            text: Raw text to escape

        Returns:
            HTML-escaped text
        """
        return html.escape(text, quote=True)

    # Document and structure nodes

    def render_document(self, node: Document) -> str:
        """Render document node."""
        return self.render_children(node)

    def render_heading(self, node: Heading) -> str:
        """Render heading node."""
        level = node.level
        content = self.render_children(node)
        attrs = self._render_attrs(node.attrs)
        return f"<h{level}{attrs}>{content}</h{level}>\n"

    def render_paragraph(self, node: Paragraph) -> str:
        """Render paragraph node."""
        content = self.render_children(node)
        if not content.strip():
            return ""
        attrs = self._render_attrs(node.attrs)
        return f"<p{attrs}>{content}</p>\n"

    def render_blockquote(self, node: BlockQuote) -> str:
        """Render blockquote node."""
        content = self.render_children(node)
        attrs = self._render_attrs(node.attrs)
        return f"<blockquote{attrs}>\n{content}</blockquote>\n"

    def render_horizontal_rule(self, node: HorizontalRule) -> str:
        """Render horizontal rule node."""
        attrs = self._render_attrs(node.attrs)
        if self.xhtml:
            return f"<hr{attrs} />\n"
        return f"<hr{attrs}>\n"

    # Text nodes

    def render_text(self, node: Text) -> str:
        """Render text node."""
        text = node.content or ""
        text = self.escape(text)

        # Handle line breaks
        if self.breaks:
            text = text.replace("\n", "<br>\n")

        # Smart typography
        if self.typographer:
            text = self._apply_typographer(text)

        return text

    def render_emphasis(self, node: Emphasis) -> str:
        """Render emphasis (italic) node."""
        content = self.render_children(node)
        attrs = self._render_attrs(node.attrs)
        return f"<em{attrs}>{content}</em>"

    def render_strong(self, node: Strong) -> str:
        """Render strong (bold) node."""
        content = self.render_children(node)
        attrs = self._render_attrs(node.attrs)
        return f"<strong{attrs}>{content}</strong>"

    # Code nodes

    def render_code_block(self, node: CodeBlock) -> str:
        """Render code block node."""
        code = self.escape(node.content or "")
        attrs = node.attrs.copy()

        # Add language class if specified
        if node.language:
            lang_class = f"{self.lang_prefix}{node.language}"
            if "class" in attrs:
                attrs["class"] += f" {lang_class}"
            else:
                attrs["class"] = lang_class

        attrs_str = self._render_attrs(attrs)
        return f"<pre><code{attrs_str}>{code}</code></pre>\n"

    def render_inline_code(self, node: InlineCode) -> str:
        """Render inline code node."""
        code = self.escape(node.content or "")
        attrs = self._render_attrs(node.attrs)
        return f"<code{attrs}>{code}</code>"

    # Link and image nodes

    def render_link(self, node: Link) -> str:
        """Render link node."""
        content = self.render_children(node)
        attrs = node.attrs.copy()
        attrs["href"] = self.escape(node.href)
        if node.title:
            attrs["title"] = self.escape(node.title)
        attrs_str = self._render_attrs(attrs)
        return f"<a{attrs_str}>{content}</a>"

    def render_image(self, node: Image) -> str:
        """Render image node."""
        attrs = node.attrs.copy()
        attrs["src"] = self.escape(node.src)
        attrs["alt"] = self.escape(node.alt)
        if node.title:
            attrs["title"] = self.escape(node.title)
        attrs_str = self._render_attrs(attrs)

        if self.xhtml:
            return f"<img{attrs_str} />"
        return f"<img{attrs_str}>"

    # List nodes

    def render_list(self, node: List) -> str:
        """Render list node."""
        self.context.enter_list(node.tight)

        tag = "ol" if node.ordered else "ul"
        attrs = {}
        if node.ordered and node.start and node.start != 1:
            attrs["start"] = str(node.start)

        # Merge with node attributes
        attrs.update(node.attrs)
        attrs_str = self._render_attrs(attrs)
        content = self.render_children(node)

        self.context.exit_list()
        return f"<{tag}{attrs_str}>\n{content}</{tag}>\n"

    def render_list_item(self, node: ListItem) -> str:
        """Render list item node."""
        content = self.render_children(node)
        attrs = self._render_attrs(node.attrs)

        # In tight lists, strip paragraph tags
        if self.context.tight_list:
            content = content.strip()
            if content.startswith("<p>") and content.endswith("</p>"):
                content = content[3:-4]

        return f"<li{attrs}>{content}</li>\n"

    # Table nodes

    def render_table(self, node: Table) -> str:
        """Render table node."""
        self.context.enter_table()

        attrs = self._render_attrs(node.attrs)

        # Separate header and body rows
        header_rows = []
        body_rows = []
        in_header = True

        for child in node.children:
            if isinstance(child, TableRow):
                if in_header and all(
                    isinstance(cell, TableCell) and cell.header for cell in child.children
                ):
                    header_rows.append(child)
                else:
                    in_header = False
                    body_rows.append(child)

        # Build table HTML
        html_parts = [f"<table{attrs}>"]

        if header_rows:
            html_parts.append("<thead>")
            for row in header_rows:
                html_parts.append(self.render_node(row))
            html_parts.append("</thead>")

        if body_rows:
            html_parts.append("<tbody>")
            for row in body_rows:
                html_parts.append(self.render_node(row))
            html_parts.append("</tbody>")

        html_parts.append("</table>\n")

        self.context.exit_table()
        return "\n".join(html_parts)

    def render_table_row(self, node: TableRow) -> str:
        """Render table row node."""
        content = self.render_children(node)
        attrs = self._render_attrs(node.attrs)
        return f"<tr{attrs}>\n{content}</tr>"

    def render_table_cell(self, node: TableCell) -> str:
        """Render table cell node."""
        tag = "th" if node.header else "td"
        attrs = node.attrs.copy()

        if node.align:
            style = attrs.get("style", "")
            if style and not style.endswith(";"):
                style += "; "
            style += f"text-align: {node.align};"
            attrs["style"] = style

        attrs_str = self._render_attrs(attrs)
        content = self.render_children(node)
        return f"<{tag}{attrs_str}>{content}</{tag}>\n"

    # Helper methods

    def _render_attrs(self, attrs: dict[str, Any]) -> str:
        """Render HTML attributes.

        Args:
            attrs: Dictionary of attributes

        Returns:
            HTML attribute string (including leading space if non-empty)
        """
        if not attrs:
            return ""

        parts = []
        for key, value in attrs.items():
            if value is True:
                parts.append(key)
            elif value is False or value is None:
                continue
            else:
                escaped_value = self.escape(str(value))
                parts.append(f'{key}="{escaped_value}"')

        if parts:
            return " " + " ".join(parts)
        return ""

    def _apply_typographer(self, text: str) -> str:
        """Apply smart typography transformations.

        Args:
            text: Text to transform

        Returns:
            Text with smart quotes and other typography
        """
        # Basic smart quotes
        if len(self.quotes) >= 4:
            # For now, skip smart quote replacement due to encoding issues
            pass

        # Other typography
        text = text.replace("--", "—")  # Em dash
        return text.replace("...", "…")  # Ellipsis


# Register the renderer
RendererRegistry.register("html", HTMLRenderer)
