# this_file: marktripy/__init__.py
"""marktripy: A Python package for converting Markdown to AST and back to Markdown."""

try:
    from marktripy._version import __version__
except ImportError:  # running from a source tree without a build
    __version__ = "0.0.0"
__author__ = "Adam Twardoch"

from loguru import logger

# Configure default logger
logger.disable("marktripy")  # Disabled by default, users can enable
