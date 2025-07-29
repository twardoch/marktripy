# this_file: marktripy/renderers/base.py
"""Abstract renderer interface for marktripy."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from loguru import logger

from marktripy.core.ast import ASTNode, Document


class Renderer(ABC):
    """Abstract base class for AST renderers.

    Renderers convert an AST back into a specific output format
    (e.g., HTML, Markdown, or other formats).
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize renderer with optional configuration.

        Args:
            config: Renderer-specific configuration options
        """
        self.config = config or {}
        logger.debug(f"Initialized {self.__class__.__name__} with config: {self.config}")

    @abstractmethod
    def render(self, ast: Document) -> str:
        """Render an AST to the output format.

        Args:
            ast: The AST to render

        Returns:
            The rendered output as a string
        """

    @abstractmethod
    def render_node(self, node: ASTNode) -> str:
        """Render a single AST node.

        This method should handle dispatching to specific node type
        rendering methods.

        Args:
            node: The node to render

        Returns:
            The rendered node output
        """

    def render_children(self, node: ASTNode) -> str:
        """Render all children of a node.

        Default implementation concatenates child renderings.
        Can be overridden for custom behavior.

        Args:
            node: The parent node

        Returns:
            Concatenated rendering of all children
        """
        return "".join(self.render_node(child) for child in node.children)

    def escape(self, text: str) -> str:
        """Escape text for the output format.

        Should be overridden by subclasses to provide format-specific
        escaping (e.g., HTML entities, Markdown special characters).

        Args:
            text: Raw text to escape

        Returns:
            Escaped text safe for output
        """
        return text

    def get_indent(self, level: int) -> str:
        """Get indentation string for a given level.

        Args:
            level: Indentation level

        Returns:
            Indentation string
        """
        indent_str = self.config.get("indent", "  ")
        return indent_str * level


class RendererError(Exception):
    """Base exception for renderer errors."""


class RenderContext:
    """Context object passed during rendering.

    Maintains state that may be needed during the rendering process,
    such as the current list depth, whether we're in a table, etc.
    """

    def __init__(self):
        """Initialize render context."""
        self.list_depth = 0
        self.in_table = False
        self.in_code_block = False
        self.tight_list = False
        self.custom_data: dict[str, Any] = {}

    def enter_list(self, tight: bool = True) -> None:
        """Enter a list context."""
        self.list_depth += 1
        self.tight_list = tight
        logger.debug(f"Entered list, depth={self.list_depth}, tight={tight}")

    def exit_list(self) -> None:
        """Exit a list context."""
        self.list_depth = max(0, self.list_depth - 1)
        logger.debug(f"Exited list, depth={self.list_depth}")

    def enter_table(self) -> None:
        """Enter a table context."""
        self.in_table = True
        logger.debug("Entered table")

    def exit_table(self) -> None:
        """Exit a table context."""
        self.in_table = False
        logger.debug("Exited table")

    def enter_code_block(self) -> None:
        """Enter a code block context."""
        self.in_code_block = True
        logger.debug("Entered code block")

    def exit_code_block(self) -> None:
        """Exit a code block context."""
        self.in_code_block = False
        logger.debug("Exited code block")

    def set_data(self, key: str, value: Any) -> None:
        """Store custom data in the context."""
        self.custom_data[key] = value

    def get_data(self, key: str, default: Any = None) -> Any:
        """Retrieve custom data from the context."""
        return self.custom_data.get(key, default)


class RendererRegistry:
    """Registry for available renderer implementations."""

    _renderers: dict[str, type[Renderer]] = {}

    @classmethod
    def register(cls, name: str, renderer_class: type[Renderer]) -> None:
        """Register a renderer implementation.

        Args:
            name: Name to register the renderer under
            renderer_class: Renderer class to register
        """
        if not issubclass(renderer_class, Renderer):
            raise TypeError(f"{renderer_class} must be a subclass of Renderer")

        cls._renderers[name] = renderer_class
        logger.info(f"Registered renderer: {name} -> {renderer_class.__name__}")

    @classmethod
    def get(cls, name: str) -> type[Renderer]:
        """Get a registered renderer class.

        Args:
            name: Name of the renderer to retrieve

        Returns:
            The renderer class

        Raises:
            KeyError: If renderer name is not registered
        """
        if name not in cls._renderers:
            raise KeyError(
                f"Renderer '{name}' not registered. Available: {list(cls._renderers.keys())}"
            )
        return cls._renderers[name]

    @classmethod
    def create(cls, name: str, config: dict[str, Any] | None = None) -> Renderer:
        """Create a renderer instance.

        Args:
            name: Name of the renderer to create
            config: Renderer configuration

        Returns:
            Renderer instance
        """
        renderer_class = cls.get(name)
        return renderer_class(config)

    @classmethod
    def list_renderers(cls) -> list[str]:
        """List all registered renderer names.

        Returns:
            List of renderer names
        """
        return list(cls._renderers.keys())
