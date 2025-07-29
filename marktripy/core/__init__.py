# this_file: marktripy/core/__init__.py
"""Core abstractions and interfaces for marktripy."""

from marktripy.core.ast import ASTNode
from marktripy.core.parser import Parser

__all__ = ["ASTNode", "Parser"]
