# this_file: marktripy/extensions/base.py
"""Extension system base classes for marktripy."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from loguru import logger

from marktripy.core.ast import ASTNode
from marktripy.core.parser import Parser
from marktripy.renderers.base import Renderer


class Extension(ABC):
    """Abstract base class for marktripy extensions.

    Extensions can modify parser behavior, add new syntax constructs,
    transform the AST, and customize rendering.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize extension with optional configuration.

        Args:
            config: Extension-specific configuration options
        """
        self.config = config or {}
        self.name = self.get_name()
        logger.debug(f"Initialized extension '{self.name}' with config: {self.config}")

    @abstractmethod
    def get_name(self) -> str:
        """Get the extension name.

        Returns:
            Extension name (should be unique)
        """

    @abstractmethod
    def get_description(self) -> str:
        """Get a human-readable description of the extension.

        Returns:
            Description string
        """

    def get_dependencies(self) -> list[str]:
        """Get list of extension names this extension depends on.

        Returns:
            List of extension names that must be loaded first
        """
        return []

    def register_inline_rule(self, parser: Parser) -> None:  # noqa: B027
        """Register inline parsing rules with the parser.

        Override this to add custom inline syntax (e.g., ++kbd++).

        Args:
            parser: Parser to register rules with
        """
        pass  # Hook method for subclasses to override

    def register_block_rule(self, parser: Parser) -> None:  # noqa: B027
        """Register block parsing rules with the parser.

        Override this to add custom block syntax (e.g., custom containers).

        Args:
            parser: Parser to register rules with
        """
        pass  # Hook method for subclasses to override

    def transform_ast(self, ast: ASTNode) -> ASTNode:
        """Transform the AST after parsing.

        Override this to modify the AST structure.

        Args:
            ast: The AST to transform

        Returns:
            The transformed AST
        """
        return ast

    def register_html_renderer(self, renderer: Renderer) -> None:  # noqa: B027
        """Register HTML rendering methods.

        Override this to customize HTML output for custom nodes.

        Args:
            renderer: HTML renderer to register methods with
        """
        pass  # Hook method for subclasses to override

    def register_markdown_renderer(self, renderer: Renderer) -> None:  # noqa: B027
        """Register Markdown rendering methods.

        Override this to customize Markdown output for custom nodes.

        Args:
            renderer: Markdown renderer to register methods with
        """
        pass  # Hook method for subclasses to override

    def setup(self) -> None:  # noqa: B027
        """Perform any one-time setup for the extension.

        Called when the extension is first loaded.
        """
        pass  # Hook method for subclasses to override

    def teardown(self) -> None:  # noqa: B027
        """Perform any cleanup when the extension is unloaded.

        Called when the extension is being removed.
        """
        pass  # Hook method for subclasses to override


class ExtensionManager:
    """Manages loading and configuring extensions."""

    def __init__(self):
        """Initialize the extension manager."""
        self.extensions: dict[str, Extension] = {}
        self.load_order: list[str] = []
        logger.debug("Initialized ExtensionManager")

    def register(self, extension: Extension) -> None:
        """Register an extension.

        Args:
            extension: Extension instance to register

        Raises:
            ValueError: If extension name is already registered
        """
        name = extension.get_name()
        if name in self.extensions:
            raise ValueError(f"Extension '{name}' is already registered")

        # Check dependencies
        for dep in extension.get_dependencies():
            if dep not in self.extensions:
                raise ValueError(f"Extension '{name}' depends on '{dep}' which is not loaded")

        self.extensions[name] = extension
        self.load_order.append(name)
        extension.setup()
        logger.info(f"Registered extension: {name}")

    def unregister(self, name: str) -> None:
        """Unregister an extension.

        Args:
            name: Name of extension to unregister

        Raises:
            KeyError: If extension is not registered
        """
        if name not in self.extensions:
            raise KeyError(f"Extension '{name}' is not registered")

        # Check if other extensions depend on this one
        for ext_name, ext in self.extensions.items():
            if ext_name != name and name in ext.get_dependencies():
                raise ValueError(
                    f"Cannot unregister '{name}': extension '{ext_name}' depends on it"
                )

        extension = self.extensions[name]
        extension.teardown()
        del self.extensions[name]
        self.load_order.remove(name)
        logger.info(f"Unregistered extension: {name}")

    def get(self, name: str) -> Extension:
        """Get a registered extension.

        Args:
            name: Name of extension to retrieve

        Returns:
            Extension instance

        Raises:
            KeyError: If extension is not registered
        """
        if name not in self.extensions:
            raise KeyError(f"Extension '{name}' is not registered")
        return self.extensions[name]

    def list_extensions(self) -> list[str]:
        """List all registered extension names in load order.

        Returns:
            List of extension names
        """
        return self.load_order.copy()

    def apply_parser_extensions(self, parser: Parser) -> None:
        """Apply all parser-related extensions.

        Args:
            parser: Parser to extend
        """
        for name in self.load_order:
            extension = self.extensions[name]
            extension.register_inline_rule(parser)
            extension.register_block_rule(parser)
            logger.debug(f"Applied parser extensions from '{name}'")

    def apply_ast_transformations(self, ast: ASTNode) -> ASTNode:
        """Apply all AST transformations from extensions.

        Args:
            ast: AST to transform

        Returns:
            Transformed AST
        """
        result = ast
        for name in self.load_order:
            extension = self.extensions[name]
            result = extension.transform_ast(result)
            logger.debug(f"Applied AST transformation from '{name}'")
        return result

    def apply_renderer_extensions(self, renderer: Renderer, format: str = "html") -> None:
        """Apply all renderer-related extensions.

        Args:
            renderer: Renderer to extend
            format: Output format ('html' or 'markdown')
        """
        for name in self.load_order:
            extension = self.extensions[name]
            if format == "html":
                extension.register_html_renderer(renderer)
            elif format == "markdown":
                extension.register_markdown_renderer(renderer)
            logger.debug(f"Applied {format} renderer extensions from '{name}'")
