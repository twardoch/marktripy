# this_file: marktripy/transformers/base.py
"""Abstract transformer interface for marktripy."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from loguru import logger

from marktripy.core.ast import ASTNode, Document


class Transformer(ABC):
    """Abstract base class for AST transformers.

    Transformers modify an AST in place or create a modified copy.
    They implement the visitor pattern to traverse and transform nodes.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize transformer with optional configuration.

        Args:
            config: Transformer-specific configuration options
        """
        self.config = config or {}
        logger.debug(f"Initialized {self.__class__.__name__} with config: {self.config}")

    def transform(self, ast: Document) -> Document:
        """Transform an entire AST.

        This is the main entry point. By default, it visits the root
        and returns the result.

        Args:
            ast: The AST to transform

        Returns:
            The transformed AST (may be the same object or a new one)
        """
        logger.info(f"Starting transformation with {self.__class__.__name__}")
        result = self.visit(ast)
        if result is None:
            result = ast
        logger.info(f"Completed transformation with {self.__class__.__name__}")
        return result

    def visit(self, node: ASTNode) -> ASTNode | None:
        """Visit a node and potentially transform it.

        This method dispatches to specific visit methods based on node type.
        If a specific method doesn't exist, falls back to generic_visit.

        Args:
            node: The node to visit

        Returns:
            The transformed node, or None to remove the node
        """
        method_name = f"visit_{node.type}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode) -> ASTNode:
        """Default visitor for nodes without specific handlers.

        By default, visits all children and returns the node unchanged.

        Args:
            node: The node to visit

        Returns:
            The node (potentially with transformed children)
        """
        # Transform children
        new_children = []
        for child in node.children:
            result = self.visit(child)
            if result is not None:
                new_children.append(result)

        node.children = new_children
        return node

    @abstractmethod
    def get_description(self) -> str:
        """Get a human-readable description of what this transformer does.

        Returns:
            Description string
        """


class TransformerChain:
    """Chain multiple transformers together."""

    def __init__(self, transformers: list[Transformer]):
        """Initialize transformer chain.

        Args:
            transformers: List of transformers to apply in order
        """
        self.transformers = transformers
        logger.debug(f"Created transformer chain with {len(transformers)} transformers")

    def transform(self, ast: Document) -> Document:
        """Apply all transformers in sequence.

        Args:
            ast: The AST to transform

        Returns:
            The transformed AST
        """
        result = ast
        for transformer in self.transformers:
            result = transformer.transform(result)
        return result

    def add_transformer(self, transformer: Transformer) -> None:
        """Add a transformer to the chain.

        Args:
            transformer: Transformer to add
        """
        self.transformers.append(transformer)
        logger.debug(f"Added {transformer.__class__.__name__} to chain")

    def remove_transformer(self, transformer: Transformer) -> None:
        """Remove a transformer from the chain.

        Args:
            transformer: Transformer to remove
        """
        self.transformers.remove(transformer)
        logger.debug(f"Removed {transformer.__class__.__name__} from chain")


class TransformerRegistry:
    """Registry for available transformer implementations."""

    _transformers: dict[str, type[Transformer]] = {}

    @classmethod
    def register(cls, name: str, transformer_class: type[Transformer]) -> None:
        """Register a transformer implementation.

        Args:
            name: Name to register the transformer under
            transformer_class: Transformer class to register
        """
        if not issubclass(transformer_class, Transformer):
            raise TypeError(f"{transformer_class} must be a subclass of Transformer")

        cls._transformers[name] = transformer_class
        logger.info(f"Registered transformer: {name} -> {transformer_class.__name__}")

    @classmethod
    def get(cls, name: str) -> type[Transformer]:
        """Get a registered transformer class.

        Args:
            name: Name of the transformer to retrieve

        Returns:
            The transformer class

        Raises:
            KeyError: If transformer name is not registered
        """
        if name not in cls._transformers:
            raise KeyError(
                f"Transformer '{name}' not registered. Available: {list(cls._transformers.keys())}"
            )
        return cls._transformers[name]

    @classmethod
    def create(cls, name: str, config: dict[str, Any] | None = None) -> Transformer:
        """Create a transformer instance.

        Args:
            name: Name of the transformer to create
            config: Transformer configuration

        Returns:
            Transformer instance
        """
        transformer_class = cls.get(name)
        return transformer_class(config)

    @classmethod
    def list_transformers(cls) -> list[str]:
        """List all registered transformer names.

        Returns:
            List of transformer names
        """
        return list(cls._transformers.keys())

    @classmethod
    def create_chain(
        cls, names: list[str], configs: list[dict[str, Any]] | None = None
    ) -> TransformerChain:
        """Create a transformer chain from a list of names.

        Args:
            names: List of transformer names
            configs: Optional list of configurations (one per transformer)

        Returns:
            TransformerChain instance
        """
        if configs is None:
            configs = [None] * len(names)
        elif len(configs) != len(names):
            raise ValueError(
                f"Number of configs ({len(configs)}) must match "
                f"number of transformers ({len(names)})"
            )

        transformers = [
            cls.create(name, config) for name, config in zip(names, configs, strict=False)
        ]

        return TransformerChain(transformers)
