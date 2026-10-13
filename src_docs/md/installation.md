# Installation

## Requirements

- Python 3.12 or later (`requires-python = ">=3.12"` in `pyproject.toml`).
- The runtime dependencies are installed automatically:

| Package | Used for |
|---|---|
| `markdown-it-py[linkify,plugins]` | The `markdown-it` parser adapter and its optional plugins (front matter, footnotes, definition lists, task lists, attributes) |
| `mistletoe` | The `mistletoe` parser adapter |
| `loguru` | Debug logging (disabled by default) |
| `fire`, `rich` | Declared dependencies; the package does not currently use them |

## Install from PyPI

With `uv` in a project:

```bash
uv add marktripy
```

With `pip`:

```bash
pip install marktripy
```

The package has no command-line entry point, so tools such as `pipx` that install applications are not useful here.

## Check the installation

Run this one-liner. It imports the package, registers the `markdown-it` parser and parses one heading:

```bash
python -c "import marktripy; from marktripy.core.parser import ParserRegistry; from marktripy.parsers import markdown_it; print(marktripy.__version__, ParserRegistry.create('markdown-it').parse('# Hi').children[0].type)"
```

The output is the installed version number followed by the word `heading`.

`marktripy.__version__` comes from the file `marktripy/_version.py`, which the build writes from the Git tag (via `hatch-vcs`). In a source checkout that has never been built, the file is missing and `__version__` falls back to `0.0.0`.

## Install from source

Prerequisites: Git and `uv`.

1. Clone the repository:

    ```bash
    git clone https://github.com/vexyart/vexy-marktripy
    cd vexy-marktripy
    ```

2. Create the environment and install the package in editable mode with its development tools:

    ```bash
    uv sync --dev
    ```

3. Run the tests to confirm the checkout works:

    ```bash
    uv run pytest -q
    ```

The `dev` dependency group adds `pytest`, `pytest-benchmark`, `pytest-cov`, `hypothesis`, `mypy`, `ruff`, `black`, `twine` and `hatch`. See [Contributing](contributing.md) for the test and build commands.

## Turn on logging

Every module logs through `loguru`, but `marktripy/__init__.py` calls `logger.disable("marktripy")`, so nothing is printed by default. To see the debug messages while you work:

```python
from loguru import logger

logger.enable("marktripy")
```
