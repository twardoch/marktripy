# this_file: marktripy/parsers/mistletoe_parser.py
"""Mistletoe parser adapter for marktripy."""

from __future__ import annotations

from typing import Any

import mistletoe
from loguru import logger
from mistletoe import Document as MistletoeDocument
from mistletoe.block_token import (
    BlockCode,
    BlockToken,
    SetextHeading,
    ThematicBreak,
)
from mistletoe.block_token import (
    Heading as MistletoeHeading,
)
from mistletoe.block_token import (
    List as MistletoeList,
)
from mistletoe.block_token import (
    ListItem as MistletoeListItem,
)
from mistletoe.block_token import (
    Paragraph as MistletoeParagraph,
)
from mistletoe.block_token import (
    Quote as MistletoeQuote,
)
from mistletoe.block_token import (
    Table as MistletoeTable,
)
from mistletoe.block_token import (
    TableCell as MistletoeTableCell,
)
from mistletoe.block_token import (
    TableRow as MistletoeTableRow,
)
from mistletoe.span_token import (
    Emphasis as MistletoeEmphasis,
)
from mistletoe.span_token import (
    Image as MistletoeImage,
)
from mistletoe.span_token import (
    InlineCode as MistletoeCode,
)
from mistletoe.span_token import (
    Link as MistletoeLink,
)
from mistletoe.span_token import (
    RawText,
    SpanToken,
)
from mistletoe.span_token import (
    Strong as MistletoeStrong,
)

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
from marktripy.core.parser import Parser, ParserError, ParserRegistry


class MistletoeParser(Parser):
    """Parser adapter for mistletoe.

    Mistletoe provides excellent round-trip conversion support,
    making it ideal for preserving formatting.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize mistletoe parser.

        Args:
            config: Parser configuration
        """
        super().__init__(config)
        logger.info("Initialized MistletoeParser")

    def parse(self, text: str) -> Document:
        """Parse Markdown text into AST.

        Args:
            text: Markdown text to parse

        Returns:
            Document AST

        Raises:
            ParserError: If parsing fails
        """
        try:
            # Preprocess text
            text = self.preprocess(text)

            # Parse with mistletoe
            mistletoe_doc = mistletoe.Document(text)

            # Convert to our AST
            doc = self._convert_document(mistletoe_doc)

            # Postprocess
            return self.postprocess(doc)

        except Exception as e:
            raise ParserError(f"Failed to parse Markdown: {e}") from e

    def _convert_document(self, mistletoe_doc: MistletoeDocument) -> Document:
        """Convert mistletoe document to our AST.

        Args:
            mistletoe_doc: Mistletoe document

        Returns:
            Our Document node
        """
        doc = Document()

        for child in mistletoe_doc.children:
            node = self._convert_block_token(child)
            if node:
                doc.add_child(node)

        return doc

    def _convert_block_token(self, token: BlockToken) -> ASTNode | None:
        """Convert a mistletoe block token to our AST node.

        Args:
            token: Mistletoe block token

        Returns:
            Converted AST node, or None if not supported
        """
        if isinstance(token, MistletoeHeading):
            return self._convert_heading(token)
        if isinstance(token, SetextHeading):
            return self._convert_setext_heading(token)
        if isinstance(token, MistletoeParagraph):
            return self._convert_paragraph(token)
        if isinstance(token, MistletoeList):
            return self._convert_list(token)
        if isinstance(token, MistletoeListItem):
            return self._convert_list_item(token)
        if isinstance(token, BlockCode):
            return self._convert_code_block(token)
        if isinstance(token, MistletoeQuote):
            return self._convert_quote(token)
        if isinstance(token, ThematicBreak):
            return HorizontalRule()
        if isinstance(token, MistletoeTable):
            return self._convert_table(token)
        logger.warning(f"Unsupported block token type: {type(token).__name__}")
        return None

    def _convert_heading(self, token: MistletoeHeading) -> Heading:
        """Convert mistletoe heading to our heading."""
        heading = Heading(level=token.level)
        self._add_inline_content(heading, token.children)
        return heading

    def _convert_setext_heading(self, token: SetextHeading) -> Heading:
        """Convert mistletoe setext heading to our heading."""
        # Setext headings are level 1 (===) or 2 (---)
        level = 1 if token.level == "=" else 2
        heading = Heading(level=level)
        self._add_inline_content(heading, token.children)
        return heading

    def _convert_paragraph(self, token: MistletoeParagraph) -> Paragraph:
        """Convert mistletoe paragraph to our paragraph."""
        para = Paragraph()
        self._add_inline_content(para, token.children)
        return para

    def _convert_list(self, token: MistletoeList) -> List:
        """Convert mistletoe list to our list."""
        # Determine if ordered
        ordered = hasattr(token, "start") and token.start is not None
        start = getattr(token, "start", None) if ordered else None
        tight = getattr(token, "tight", True)

        list_node = List(ordered=ordered, start=start, tight=tight)

        for child in token.children:
            if isinstance(child, MistletoeListItem):
                item = self._convert_list_item(child)
                if item:
                    list_node.add_child(item)

        return list_node

    def _convert_list_item(self, token: MistletoeListItem) -> ListItem:
        """Convert mistletoe list item to our list item."""
        item = ListItem()

        for child in token.children:
            if isinstance(child, BlockToken):
                node = self._convert_block_token(child)
                if node:
                    item.add_child(node)
            else:
                # Inline content
                self._add_inline_content(item, [child])

        return item

    def _convert_code_block(self, token: BlockCode) -> CodeBlock:
        """Convert mistletoe code block to our code block."""
        language = getattr(token, "language", None) or None
        content = token.children[0].content if token.children else ""
        return CodeBlock(content=content, language=language)

    def _convert_quote(self, token: MistletoeQuote) -> BlockQuote:
        """Convert mistletoe quote to our blockquote."""
        quote = BlockQuote()

        for child in token.children:
            node = self._convert_block_token(child)
            if node:
                quote.add_child(node)

        return quote

    def _convert_table(self, token: MistletoeTable) -> Table:
        """Convert mistletoe table to our table."""
        table = Table()

        # Process header if present
        if hasattr(token, "header") and token.header:
            header_row = TableRow()
            for cell in token.header.children:
                if isinstance(cell, MistletoeTableCell):
                    cell_node = self._convert_table_cell(cell, header=True)
                    header_row.add_child(cell_node)
            table.add_child(header_row)

        # Process body rows
        for row in token.children:
            if isinstance(row, MistletoeTableRow):
                row_node = self._convert_table_row(row)
                table.add_child(row_node)

        return table

    def _convert_table_row(self, token: MistletoeTableRow) -> TableRow:
        """Convert mistletoe table row to our table row."""
        row = TableRow()

        for cell in token.children:
            if isinstance(cell, MistletoeTableCell):
                cell_node = self._convert_table_cell(cell)
                row.add_child(cell_node)

        return row

    def _convert_table_cell(self, token: MistletoeTableCell, header: bool = False) -> TableCell:
        """Convert mistletoe table cell to our table cell."""
        align = getattr(token, "align", None)
        cell = TableCell(header=header, align=align)
        self._add_inline_content(cell, token.children)
        return cell

    def _add_inline_content(self, parent: ASTNode, tokens: list[SpanToken]) -> None:
        """Add inline content to a parent node.

        Args:
            parent: Parent node to add content to
            tokens: List of mistletoe span tokens
        """
        for token in tokens:
            node = self._convert_span_token(token)
            if node:
                parent.add_child(node)

    def _convert_span_token(self, token: SpanToken) -> ASTNode | None:
        """Convert a mistletoe span token to our AST node.

        Args:
            token: Mistletoe span token

        Returns:
            Converted AST node, or None if not supported
        """
        if isinstance(token, RawText):
            return Text(content=token.content)
        if isinstance(token, MistletoeEmphasis):
            em = Emphasis()
            self._add_inline_content(em, token.children)
            return em
        if isinstance(token, MistletoeStrong):
            strong = Strong()
            self._add_inline_content(strong, token.children)
            return strong
        if isinstance(token, MistletoeCode):
            return InlineCode(content=token.children[0].content)
        if isinstance(token, MistletoeLink):
            link = Link(href=token.target, title=getattr(token, "title", None))
            self._add_inline_content(link, token.children)
            return link
        if isinstance(token, MistletoeImage):
            return Image(
                src=token.target,
                alt=token.children[0].content if token.children else "",
                title=getattr(token, "title", None),
            )
        logger.warning(f"Unsupported span token type: {type(token).__name__}")
        return None

    def get_capabilities(self) -> dict[str, bool]:
        """Get parser capabilities.

        Returns:
            Dictionary with capability flags
        """
        return {
            "tables": True,
            "strikethrough": True,
            "task_lists": True,
            "footnotes": True,
            "definition_lists": False,  # Not in standard mistletoe
            "math": False,  # Requires extension
            "smart_quotes": False,
            "custom_extensions": True,
        }


# Register the parser
ParserRegistry.register("mistletoe", MistletoeParser)
