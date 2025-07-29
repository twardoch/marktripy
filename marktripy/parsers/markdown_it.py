# this_file: marktripy/parsers/markdown_it.py
"""markdown-it-py parser adapter for marktripy."""

from __future__ import annotations

from typing import Any

from loguru import logger
from markdown_it import MarkdownIt
from markdown_it.token import Token

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


class MarkdownItParser(Parser):
    """Parser implementation using markdown-it-py."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize markdown-it-py parser.

        Args:
            config: Parser configuration with options:
                - preset: Parser preset ('default', 'commonmark', 'zero')
                - options: markdown-it options dict
                - plugins: List of plugin names to enable
                - disable: List of rule names to disable
                - enable: List of rule names to enable
        """
        super().__init__(config)

        # Get configuration
        preset = self.config.get("preset", "commonmark")
        options = self.config.get("options", {})
        plugins = self.config.get("plugins", [])
        disable_rules = self.config.get("disable", [])
        enable_rules = self.config.get("enable", [])

        # Initialize markdown-it
        self.md = MarkdownIt(preset, options)

        # Enable HTML by default unless explicitly disabled
        if options.get("html", True):
            self.md.enable("html_inline")
            self.md.enable("html_block")

        # Enable/disable rules
        if disable_rules:
            self.md.disable(disable_rules)
        if enable_rules:
            self.md.enable(enable_rules)

        # Load plugins if available
        self._load_plugins(plugins)

        logger.info(f"Initialized MarkdownItParser with preset '{preset}'")

    def _load_plugins(self, plugins: list[str]) -> None:
        """Load markdown-it-py plugins.

        Args:
            plugins: List of plugin names to load
        """
        for plugin_name in plugins:
            try:
                if plugin_name == "front_matter":
                    from mdit_py_plugins.front_matter import front_matter_plugin

                    self.md.use(front_matter_plugin)
                elif plugin_name == "footnote":
                    from mdit_py_plugins.footnote import footnote_plugin

                    self.md.use(footnote_plugin)
                elif plugin_name == "deflist":
                    from mdit_py_plugins.deflist import deflist_plugin

                    self.md.use(deflist_plugin)
                elif plugin_name == "tasklists":
                    from mdit_py_plugins.tasklists import tasklists_plugin

                    self.md.use(tasklists_plugin)
                elif plugin_name == "attrs":
                    from mdit_py_plugins.attrs import attrs_plugin

                    self.md.use(attrs_plugin)
                else:
                    logger.warning(f"Unknown plugin: {plugin_name}")
                logger.debug(f"Loaded plugin: {plugin_name}")
            except ImportError:
                logger.error(f"Failed to import plugin: {plugin_name}")

    def parse(self, text: str) -> Document:
        """Parse Markdown text into an AST.

        Args:
            text: The Markdown text to parse

        Returns:
            The root Document node of the AST
        """
        try:
            # Preprocess text
            text = self.preprocess(text)

            # Parse to tokens
            tokens = self.md.parse(text)

            # Convert tokens to AST
            doc = self._tokens_to_ast(tokens)

            # Postprocess AST
            return self.postprocess(doc)

        except Exception as e:
            raise ParserError(f"Failed to parse Markdown: {e}") from e

    def _tokens_to_ast(self, tokens: list[Token]) -> Document:
        """Convert markdown-it tokens to AST.

        Args:
            tokens: List of markdown-it tokens

        Returns:
            Document node with AST
        """
        doc = Document()
        self._process_tokens(tokens, doc)
        return doc

    def _process_tokens(self, tokens: list[Token], parent: ASTNode, start_idx: int = 0) -> int:
        """Process tokens and build AST recursively.

        Args:
            tokens: List of tokens to process
            parent: Parent node to add children to
            start_idx: Starting index in token list

        Returns:
            Index after processed tokens
        """
        i = start_idx

        while i < len(tokens):
            token = tokens[i]

            # Skip hidden tokens
            if token.hidden:
                i += 1
                continue

            # Handle opening tags
            if token.nesting == 1:
                node = self._create_node_from_token(token)
                if node:
                    parent.add_child(node)
                    # Process children for container nodes
                    if token.type in [
                        "bullet_list_open",
                        "ordered_list_open",
                        "list_item_open",
                        "blockquote_open",
                        "table_open",
                        "thead_open",
                        "tbody_open",
                        "tr_open",
                        "th_open",
                        "td_open",
                        "heading_open",
                        "paragraph_open",
                        "em_open",
                        "strong_open",
                        "s_open",
                        "link_open",
                    ]:
                        i = self._process_tokens(tokens, node, i + 1)
                        continue

            # Handle closing tags
            elif token.nesting == -1:
                return i + 1

            # Handle self-closing tags and content
            else:
                # Special handling for inline tokens
                if token.type == "inline" and token.children:
                    self._process_inline_tokens(token.children, parent)
                else:
                    node = self._create_node_from_token(token)
                    if node:
                        parent.add_child(node)

            i += 1

        return i

    def _process_inline_tokens(self, tokens: list[Token], parent: ASTNode) -> None:
        """Process inline tokens with proper nesting.

        Args:
            tokens: List of inline tokens
            parent: Parent node to add children to
        """
        stack = []

        for token in tokens:
            if token.nesting == 1:
                # Opening tag - create node and push to stack
                node = self._create_node_from_token(token)
                if node:
                    if stack:
                        stack[-1].add_child(node)
                    else:
                        parent.add_child(node)
                    stack.append(node)
            elif token.nesting == -1:
                # Closing tag - pop from stack
                if stack:
                    stack.pop()
            else:
                # Content or self-closing tag
                node = self._create_node_from_token(token)
                if node:
                    if stack:
                        stack[-1].add_child(node)
                    else:
                        parent.add_child(node)

    def _create_node_from_token(self, token: Token) -> ASTNode | None:
        """Create an AST node from a token.

        Args:
            token: markdown-it token

        Returns:
            AST node or None if token should be skipped
        """
        # Content tokens
        if token.type == "text":
            return Text(content=token.content)
        if token.type == "code_inline":
            return InlineCode(content=token.content)
        if token.type == "softbreak" or token.type == "hardbreak":
            return Text(content="\n")
        if token.type == "html_inline" or token.type == "html_block":
            return Text(content=token.content)

        # Block tokens
        if token.type == "heading_open":
            level = int(token.tag[1])  # h1 -> 1, h2 -> 2, etc.
            node = Heading(level=level)
            if token.attrGet("id"):
                node.set_attr("id", token.attrGet("id"))
            return node
        if token.type == "paragraph_open":
            return Paragraph()
        if token.type == "blockquote_open":
            return BlockQuote()
        if token.type == "hr":
            return HorizontalRule()
        if token.type == "fence" or token.type == "code_block":
            language = token.info.strip() if token.info else None
            return CodeBlock(content=token.content, language=language)

        # List tokens
        if token.type == "bullet_list_open":
            tight = getattr(token, "tight", True)
            return List(ordered=False, tight=tight)
        if token.type == "ordered_list_open":
            start = token.attrGet("start")
            tight = getattr(token, "tight", True)
            return List(ordered=True, start=int(start) if start else 1, tight=tight)
        if token.type == "list_item_open":
            return ListItem()

        # Inline tokens
        if token.type == "em_open":
            return Emphasis()
        if token.type == "strong_open":
            return Strong()
        if token.type == "s_open":
            # Create a generic strikethrough node
            return ASTNode(type="strikethrough")
        if token.type == "link_open":
            href = token.attrGet("href") or ""
            title = token.attrGet("title")
            return Link(href=href, title=title)
        if token.type == "image":
            src = token.attrGet("src") or ""
            alt = token.content
            title = token.attrGet("title")
            return Image(src=src, alt=alt, title=title)

        # Table tokens
        if token.type == "table_open":
            return Table()
        if token.type in ["thead_open", "tbody_open"]:
            # These are structural tokens we can skip
            return None
        if token.type == "tr_open":
            return TableRow()
        if token.type in ["th_open", "td_open"]:
            align = token.attrGet("style")
            if align and "text-align:" in align:
                align = align.split("text-align:")[1].split(";")[0].strip()
            else:
                align = None
            return TableCell(header=(token.type == "th_open"), align=align)

        # Skip closing tags and other tokens
        return None

    def get_capabilities(self) -> dict[str, bool]:
        """Get parser capabilities.

        Returns:
            Dictionary with capability flags
        """
        return {
            "tables": "table" in self.md.get_active_rules()["block"],
            "strikethrough": "strikethrough" in self.md.get_active_rules()["inline"],
            "task_lists": any("tasklist" in str(r) for r in self.md.get_active_rules()["inline"]),
            "footnotes": any("footnote" in str(r) for r in self.md.get_active_rules()["block"]),
            "definition_lists": any(
                "deflist" in str(r) for r in self.md.get_active_rules()["block"]
            ),
            "math": False,  # Would need math plugin
            "smart_quotes": self.md.options.get("typographer", False),
            "custom_extensions": True,
        }


# Register the parser
ParserRegistry.register("markdown-it", MarkdownItParser)
