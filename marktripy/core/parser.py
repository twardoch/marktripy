# this_file: marktripy/core/parser.py
"""Abstract parser interface for marktripy."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from loguru import logger

from marktripy.core.ast import Document


class Parser(ABC):
    """Abstract base class for Markdown parsers.

    This interface defines the contract that all parser implementations
    must follow. Parsers convert Markdown text into an AST representation.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize parser with optional configuration.

        Args:
            config: Parser-specific configuration options
        """
        self.config = config or {}
        logger.debug(f"Initialized {self.__class__.__name__} with config: {self.config}")

    @abstractmethod
    def parse(self, text: str) -> Document:
        """Parse Markdown text into an AST.

        Args:
            text: The Markdown text to parse

        Returns:
            The root Document node of the AST
        """

    @abstractmethod
    def get_capabilities(self) -> dict[str, bool]:
        """Get parser capabilities.

        Returns a dictionary indicating which features this parser supports.

        Returns:
            Dictionary with capability flags like:
            - 'tables': Table support
            - 'strikethrough': Strikethrough syntax
            - 'task_lists': Task list checkboxes
            - 'footnotes': Footnote references
            - 'definition_lists': Definition list syntax
            - 'math': Math expressions
            - 'smart_quotes': Smart typography
            - 'custom_extensions': Custom extension support
        """

    def validate_markdown(self, text: str) -> list[str]:
        """Validate Markdown syntax and return any errors.

        Default implementation just tries to parse and catches exceptions.
        Subclasses can override for more detailed validation.

        Args:
            text: The Markdown text to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        try:
            self.parse(text)
        except Exception as e:
            errors.append(str(e))
        return errors

    def preprocess(self, text: str) -> str:
        """Preprocess Markdown text before parsing.

        Can be overridden by subclasses to normalize text, handle
        special cases, or apply transformations.

        Args:
            text: Raw Markdown text

        Returns:
            Preprocessed text ready for parsing
        """
        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Ensure text ends with newline
        if text and not text.endswith("\n"):
            text += "\n"

        logger.debug(f"Preprocessed text: {len(text)} characters")
        return text

    def postprocess(self, ast: Document) -> Document:
        """Postprocess AST after parsing.

        Can be overridden by subclasses to apply transformations,
        validate the AST structure, or enrich nodes with metadata.

        Args:
            ast: The parsed AST

        Returns:
            The postprocessed AST
        """
        logger.debug(f"Postprocessed AST with {len(ast.children)} top-level nodes")
        return ast


class ParserError(Exception):
    """Base exception for parser errors."""

    def __init__(self, message: str, line: int | None = None, column: int | None = None):
        """Initialize parser error.

        Args:
            message: Error description
            line: Line number where error occurred (1-based)
            column: Column number where error occurred (1-based)
        """
        self.line = line
        self.column = column

        if line is not None and column is not None:
            full_message = f"{message} at line {line}, column {column}"
        elif line is not None:
            full_message = f"{message} at line {line}"
        else:
            full_message = message

        super().__init__(full_message)


class ParserRegistry:
    """Registry for available parser implementations."""

    _parsers: dict[str, type[Parser]] = {}

    @classmethod
    def register(cls, name: str, parser_class: type[Parser]) -> None:
        """Register a parser implementation.

        Args:
            name: Name to register the parser under
            parser_class: Parser class to register
        """
        if not issubclass(parser_class, Parser):
            raise TypeError(f"{parser_class} must be a subclass of Parser")

        cls._parsers[name] = parser_class
        logger.info(f"Registered parser: {name} -> {parser_class.__name__}")

    @classmethod
    def get(cls, name: str) -> type[Parser]:
        """Get a registered parser class.

        Args:
            name: Name of the parser to retrieve

        Returns:
            The parser class

        Raises:
            KeyError: If parser name is not registered
        """
        if name not in cls._parsers:
            raise KeyError(
                f"Parser '{name}' not registered. Available: {list(cls._parsers.keys())}"
            )
        return cls._parsers[name]

    @classmethod
    def create(cls, name: str, config: dict[str, Any] | None = None) -> Parser:
        """Create a parser instance.

        Args:
            name: Name of the parser to create
            config: Parser configuration

        Returns:
            Parser instance
        """
        parser_class = cls.get(name)
        return parser_class(config)

    @classmethod
    def list_parsers(cls) -> list[str]:
        """List all registered parser names.

        Returns:
            List of parser names
        """
        return list(cls._parsers.keys())
