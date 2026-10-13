# marktripy

`marktripy` turns Markdown text into a tree of Python objects, lets you change that tree, and writes it back out as Markdown or HTML. The PyPI package is called `marktripy`; the source lives in the `vexyart/vexy-marktripy` repository.

```python
from marktripy.core.parser import ParserRegistry
from marktripy.parsers import markdown_it  # importing the module registers the parser
from marktripy.renderers.markdown import MarkdownRenderer

parser = ParserRegistry.create("markdown-it")
doc = parser.parse("# Hello\n\nThis is **bold** text.\n")

for node in doc.find_all("heading"):
    node.level += 1

print(MarkdownRenderer().render(doc))
# ## Hello
#
# This is **bold** text.
```

## What the package does

Every operation follows the same three stages:

1. **Parse.** A parser adapter reads Markdown text and builds a `Document` node. Two adapters ship with the package: one built on `markdown-it-py` and one built on `mistletoe`.
2. **Change.** You edit the tree directly, or you run *transformers* (heading level changes, heading IDs, a table of contents, reference-style links) and *extensions* (strikethrough, task lists, `++key++` keyboard notation).
3. **Render.** A renderer walks the tree and produces text. `MarkdownRenderer` writes Markdown, `HTMLRenderer` writes HTML.

All three stages share one node model, described in [The AST](ast.md). Because both parsers produce the same node types, a transformer or renderer does not need to know which parser built the tree.

## Project status

The package is at an early stage (`Development Status :: 3 - Alpha` in `pyproject.toml`). The core parse → change → render loop works and is covered by the test suite, but some parts are incomplete:

- There is no top-level convenience API. You import classes from their modules, for example `marktripy.core.parser.ParserRegistry`. The names `parse_markdown`, `render_markdown` and `markdown_to_html` shown in older README examples do not exist.
- There is no command-line tool.
- Several behaviours have known gaps, for example table bodies from the `markdown-it` adapter and `[[TOC]]` marker replacement. See [Known limitations](limitations.md) before you rely on a feature.

## Where to go next

| If you want to… | Read |
|---|---|
| Install the package | [Installation](installation.md) |
| Run a first parse and render | [Quickstart](quickstart.md) |
| Understand the node classes and tree methods | [The AST](ast.md) |
| Choose and configure a parser | [Parsers](parsers.md) |
| Control Markdown or HTML output | [Renderers](renderers.md) |
| Shift headings, add IDs, build a TOC | [Transformers](transformers.md) |
| Add strikethrough, task lists or `++key++` | [Extensions](extensions.md) |
| Check a tree for structural problems | [Validation and utilities](validation.md) |
| Look up a class or function | [API reference](api.md) |
| See how the modules fit together | [Architecture](architecture.md) |
| Run the tests or build the docs | [Contributing](contributing.md) |
