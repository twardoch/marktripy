# Changelog

All notable changes to marktripy will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-01-28

### Added
- Complete markdown-it-py parser adapter implementation
  - Token to AST conversion with full inline content support
  - Proper handling of all node types including nested structures
  - Plugin loading support for markdown-it-py extensions
- Full HTML renderer implementation
  - Support for all AST node types
  - Proper HTML escaping and attribute rendering
  - Context management for nested structures (lists, tables)
  - Configurable options (xhtml, breaks, langPrefix, etc.)
- Comprehensive test suite with 12 passing tests
  - Parser registration and functionality tests
  - HTML rendering tests including edge cases
  - AST manipulation tests (traversal, cloning, attributes)
- CI/CD pipeline with GitHub Actions
  - Multi-version Python testing (3.10, 3.11, 3.12)
  - Automated linting and formatting checks
  - Code coverage reporting with codecov
  - Release automation workflow
- Development tooling improvements
  - mypy configuration for type checking
  - Dependabot configuration for dependency updates
  - twine added for package publishing

### Fixed
- Heading content parsing now correctly processes inline tokens
- Token.tight attribute handled with safe fallback
- ASTNode clone method uses copy.copy for proper inheritance
- Inline formatting (strong/em) content captured correctly
- HTML attribute rendering excludes internal properties
- Walk method returns correct node count
- All ruff linter warnings resolved

### Changed
- Updated TODO.md to mark Phase 1 tasks as completed
- Enhanced WORK.md with detailed progress tracking

## [0.1.0] - 2025-01-28

### Added
- Initial project structure created with `uv` package manager
- Comprehensive `pyproject.toml` with all dependencies and tool configurations
- Core package architecture with modules: core, parsers, renderers, transformers, extensions, utils
- Abstract base classes and interfaces:
  - `ASTNode` hierarchy with all common Markdown element types (Document, Heading, Paragraph, Text, Emphasis, Strong, Link, Image, CodeBlock, InlineCode, List, ListItem, BlockQuote, HorizontalRule, Table, TableRow, TableCell)
  - `Parser` interface with preprocessing/postprocessing hooks and registry pattern
  - `Renderer` interface with context management and registry pattern
  - `Transformer` interface implementing visitor pattern with chaining support
  - `Extension` system with comprehensive hooks for parser rules, AST transformation, and rendering
- Registry pattern implemented across all major components for extensibility
- Integrated logging throughout using loguru
- Full type hints and comprehensive documentation for all classes and methods
- Development environment set up with Python 3.12, pytest, ruff, black, and hypothesis

### Infrastructure
- Configured pytest with coverage reporting
- Set up ruff linting with comprehensive rule selection
- Configured black code formatting with 100-character line length
- Added tool configurations for consistent development experience

### Dependencies
- Core: fire (CLI), rich (terminal UI), markdown-it-py (parser), mistletoe (parser), loguru (logging)
- Development: pytest, pytest-cov, ruff, black, hypothesis, mypy, twine