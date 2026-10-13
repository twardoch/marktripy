# Quickstart

This page follows one small document through a parse, two changes and two renders. Every output shown was produced by running the code against the current source.

Prerequisite: `marktripy` is installed ([Installation](installation.md)).

## 1. Create a parser

Parsers are registered by name when their module is imported. Import the module, then ask the registry for an instance:

```python
from marktripy.core.parser import ParserRegistry
from marktripy.parsers import markdown_it  # registers "markdown-it"

parser = ParserRegistry.create("markdown-it")
```

You can also construct the class directly: `markdown_it.MarkdownItParser()`.

## 2. Parse Markdown

```python
doc = parser.parse("# Hello\n\nThis is **bold** text.\n")
```

`doc` is a `Document` node. Its tree looks like this:

```text
document
  heading            level=1
    text             'Hello'
  paragraph
    text             'This is '
    strong
      text           'bold'
    text             ' text.'
```

Inline formatting is a node with children: `**bold**` became a `strong` node that contains a `text` node.

## 3. Change the tree

Every node has `walk()` (all nodes, depth first) and `find_all(type)` (all nodes of one type). Headings carry their level in the `level` attribute:

```python
for heading in doc.find_all("heading"):
    heading.level += 1
```

The `Heading` constructor rejects levels outside 1–6, but assigning `level` afterwards is not checked. The transformers in [Transformers](transformers.md) clamp levels for you.

## 4. Render Markdown

```python
from marktripy.renderers.markdown import MarkdownRenderer

print(MarkdownRenderer().render(doc))
```

Output:

```markdown
## Hello

This is **bold** text.
```

## 5. Render HTML

```python
from marktripy.renderers.html import HTMLRenderer

print(HTMLRenderer().render(doc))
```

Output:

```html
<h2>Hello</h2>
<p>This is <strong>bold</strong> text.</p>
```

## 6. Add heading IDs and a table of contents

The transformer modules provide one-call helper functions.

```python
from marktripy.transformers.id_generator import add_heading_ids
from marktripy.transformers.toc import generate_toc

doc = parser.parse("# Intro\n\n## Setup\n\n## Setup\n\n### Café & Crème\n")
add_heading_ids(doc)            # changes doc in place
doc = generate_toc(doc)         # returns a new Document with the TOC inserted

print(MarkdownRenderer().render(doc))
```

Output:

```markdown
# Intro

## Table of Contents

- [Intro](#intro)
   - [Setup](#setup)
   - [Setup](#setup-1)
      - [Café & Crème](#cafe-creme)

## Setup

## Setup

### Café & Crème
```

What happened:

- `add_heading_ids` slugified each heading's text. The second `Setup` got the suffix `-1` so IDs stay unique, and the accents were stripped (`Café & Crème` → `cafe-creme`).
- `generate_toc` collected headings of levels 1–3, built a nested list of links, and inserted it after the first level-1 heading. It returned a copy of the document, so keep the return value.

The IDs are stored in each heading's `attrs` and appear in HTML output (`<h2 id="setup">Setup</h2>`). Markdown has no heading-ID syntax, so `MarkdownRenderer` does not write them.

## 7. Enable GFM features

Strikethrough and task lists need two things: a parser preset that recognises the syntax, and the extension that turns the parsed result into proper nodes and renders them.

```python
from marktripy.extensions.base import ExtensionManager
from marktripy.extensions.gfm import GFMExtension

parser = ParserRegistry.create("markdown-it", {"preset": "default"})
html = HTMLRenderer()

manager = ExtensionManager()
manager.register(GFMExtension())
manager.apply_renderer_extensions(html, "html")

doc = parser.parse("~~old~~ new\n\n- [ ] todo\n- [x] done\n")
doc = manager.apply_ast_transformations(doc)
print(html.render(doc))
```

Output (line breaks as produced):

```html
<p><del>old</del> new</p>
<ul>
<li><input type="checkbox" disabled> todo</li><li><input type="checkbox" disabled checked> done</li></ul>
```

See [Extensions](extensions.md) for the order of these calls and for the `++key++` extension.

## Next steps

- [The AST](ast.md) lists every node class and tree method.
- [Parsers](parsers.md) explains presets, plugins and the `mistletoe` adapter.
- [Known limitations](limitations.md) lists the cases that do not round-trip yet.
