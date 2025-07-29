# this_file: marktripy/__init__.py
"""marktripy: A Python package for converting Markdown to AST and back to Markdown."""

__version__ = "0.1.0"
__author__ = "Adam"

from loguru import logger

# Configure default logger
logger.disable("marktripy")  # Disabled by default, users can enable
