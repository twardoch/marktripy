# Transformers

A transformer takes a `Document`, changes it, and returns a `Document`. The package ships four, each with helper functions for one-line use.

| Module | Classes | Helper functions |
|---|---|---|
| `marktripy.transformers.heading` | `HeadingLevelTransformer`, `HeadingShifter`, `HeadingNormalizer` | `increase_heading_levels`, `decrease_heading_levels`, `normalize_headings` |
| `marktripy.transformers.id_generator` | `IDGeneratorTransformer`, `HeadingIDGenerator`, `TableIDGenerator` | `add_heading_ids`, `add_ids_to_elements` |
| `marktripy.transformers.toc` | `TOCGenerator` | `generate_toc`, `extract_toc` |
| `marktripy.transformers.link_reference` | `LinkReferenceTransformer`, `LinkCollector` | `convert_to_reference_links`, `collect_links` |

!!! warning "Always keep the return value"
    Most transformers change the tree in place and return the same object. `TOCGenerator` with insertion enabled returns a **copy** with the TOC added and leaves the input unchanged. Write `doc = transformer.transform(doc)` every time and you do not need to remember which is which.

The examples on this page use this setup:

```python
from marktripy.core.parser import ParserRegistry
from marktripy.parsers import markdown_it
from marktripy.renderers.markdown import MarkdownRenderer

parser = ParserRegistry.create("markdown-it")
md = MarkdownRenderer()
```

## Heading levels

`HeadingLevelTransformer(config)` changes every heading's level. Configuration keys:

| Key | Default | Meaning |
|---|---|---|
| `operation` | `"increase"` | `"increase"`, `"decrease"`, `"set"` or `"normalize"` |
| `amount` | `1` | Step for `increase` and `decrease` |
| `level` | `1` | Target level for `set` |
| `min_level` | `1` | Lowest allowed result |
| `max_level` | `6` | Highest allowed result |

Every result is clamped to `min_level`…`max_level`, so increasing a level 6 heading leaves it at 6.

`normalize` maps the distinct levels in use, in order, to 1, 2, 3…:

```python
from marktripy.transformers.heading import normalize_headings

doc = parser.parse("### A\n\n##### B\n\n### C\n")
normalize_headings(doc)
print(md.render(doc))
```

Output:

```markdown
# A

## B

# C
```

The levels 3 and 5 became 1 and 2. Gaps disappear, but the relative order is kept.

Shortcuts:

- `HeadingShifter(shift)` increases for a positive `shift` and decreases for a negative one.
- `HeadingNormalizer()` is `HeadingLevelTransformer({"operation": "normalize"})`.
- `increase_heading_levels(ast, amount=1)` and `decrease_heading_levels(ast, amount=1)` build the transformer and run it.

## Heading IDs

`IDGeneratorTransformer(config)` stores a unique `id` attribute on matching nodes. Configuration keys:

| Key | Default | Meaning |
|---|---|---|
| `prefix` | `""` | Text prepended to the heading text before slugifying, joined with `separator` |
| `separator` | `"-"` | Joiner between `prefix` and the text |
| `overwrite` | `False` | Replace IDs that are already present |
| `target_elements` | `["heading"]` | Node types that receive IDs |

The ID is built by `generate_id()` from `marktripy.utils.slugify`:

1. Extract the node's plain text (`Café & Crème`).
2. Normalise to ASCII, lower-case, drop everything except letters, digits, spaces and hyphens (`cafe  creme`).
3. Collapse runs of spaces and hyphens into `-` (`cafe-creme`).
4. If the slug is empty, use `section`. If it is already used in this document, append `-1`, `-2`, … until it is unique.

When `overwrite` is `False`, IDs already in the tree are collected first, so new IDs never collide with them.

```python
from marktripy.transformers.id_generator import add_heading_ids

doc = parser.parse("# Intro\n\n## Setup\n\n## Setup\n")
add_heading_ids(doc, prefix="doc")
print([h.get_attr("id") for h in doc.find_all("heading")])
# ['doc-intro', 'doc-setup', 'doc-setup-1']
```

`HeadingIDGenerator(prefix="", overwrite=False)` targets headings only. `TableIDGenerator(prefix="table", overwrite=False)` targets tables. Tables have no text of their own, so a table's ID is built from the joined text of the cells inside the `Table` node: header cells `a` and `b` give `table-ab`. `add_ids_to_elements(ast, elements, prefix="", overwrite=False)` lets you pass any list of node types.

The IDs appear in HTML output. `MarkdownRenderer` ignores them because Markdown has no heading-ID syntax.

## Table of contents

`TOCGenerator(config)` collects headings and builds a nested list of links. Configuration keys:

| Key | Default | Meaning |
|---|---|---|
| `min_level` | `1` | Lowest heading level to include |
| `max_level` | `3` | Highest heading level to include |
| `title` | `"Table of Contents"` | Text of a level 2 heading placed above the list. An empty string omits it. |
| `insert` | `True` | Insert the TOC into a copy of the document |
| `ordered` | `False` | Use ordered lists instead of bullet lists |
| `marker` | `"[[TOC]]"` | Paragraph text to replace with the TOC. See the note below. |
| `indent_size` | `2` | Stored but not used |

Each entry links to `#<id>` if the heading has an `id` attribute, and is plain text otherwise. Run the ID transformer first if you want links.

Where the TOC goes: directly after the first level 1 heading at the top of the document, or before the first other block. Paragraphs that start with `---` or `+++` are skipped over.

!!! note "Marker replacement does not take effect"
    The code looks for a paragraph whose only text is the `marker`, but its parent lookup never finds the paragraph, so the marker is left in place and the TOC is inserted at the default position. With `MarkdownRenderer` the leftover marker is then escaped as `\[\[TOC\]\]`. Remove the marker paragraph yourself if you use one. See [Known limitations](limitations.md).

Chain IDs and the TOC:

```python
from marktripy.transformers.base import TransformerChain
from marktripy.transformers.id_generator import HeadingIDGenerator
from marktripy.transformers.toc import TOCGenerator

doc = parser.parse("# Guide\n\n## Install\n\n## Use\n\n### Detail\n")
chain = TransformerChain([
    HeadingIDGenerator(prefix="doc"),
    TOCGenerator({"title": "Contents", "max_level": 2}),
])
print(md.render(chain.transform(doc)))
```

Output:

```markdown
# Guide

## Contents

- [Guide](#doc-guide)
   - [Install](#doc-install)
   - [Use](#doc-use)

## Install

## Use

### Detail
```

`generate_toc(ast, max_level=3, insert=True)` and `extract_toc(ast, max_level=3)` are shortcuts. `extract_toc` returns the TOC as a `Document` node (title heading plus list) without changing the input, or `None` if there are no headings in range. After any run, `TOCGenerator.get_toc()` returns the same node.

## Reference-style links

`LinkReferenceTransformer(config)` gives every inline link a reference ID and appends the definitions at the end of the document. Configuration keys:

| Key | Default | Meaning |
|---|---|---|
| `style` | `"numeric"` | `"numeric"` gives `1`, `2`, …; `"text"` slugifies the link text (up to 50 characters) |
| `dedup` | `True` | Reuse one ID for links with the same URL |
| `section_title` | `"References"` | Level 2 heading above the definitions. An empty string omits it. |
| `preserve_titles` | `True` | Keep link titles in the definitions |

The transformer sets `attrs["reference_id"]` on each `Link`. `MarkdownRenderer` then writes the link as `[text][id]`. The definitions are added as paragraphs containing text such as `[1]: https://python.org`.

!!! warning "Definitions are escaped in Markdown output"
    The definitions are plain `Text` nodes, so `MarkdownRenderer` escapes their brackets: `\[1\]: https://python.org`. The result is not a valid reference definition. See [Known limitations](limitations.md).

`collect_links(ast)` returns all `Link` nodes without changing anything:

```python
from marktripy.transformers.link_reference import collect_links

doc = parser.parse('See [Python](https://python.org) and [docs](https://python.org "Py").\n')
print([link.href for link in collect_links(doc)])
# ['https://python.org', 'https://python.org']
```

## Write your own transformer

Subclass `Transformer`, implement `get_description()`, and add `visit_<type>` methods for the node types you care about.

How the traversal works:

1. `transform(ast)` calls `visit(ast)`.
2. `visit(node)` calls `visit_<node.type>` if it exists, otherwise `generic_visit(node)`.
3. `generic_visit(node)` visits each child and keeps the returned node. A child whose visit returns `None` is removed.
4. If your `visit_<type>` method should also process the node's children, call `self.generic_visit(node)` inside it.

This transformer removes all images and upper-cases link text:

```python
from marktripy.transformers.base import Transformer


class Tidy(Transformer):
    def get_description(self) -> str:
        return "Remove images, upper-case link text"

    def visit_image(self, node):
        return None                      # drop the node

    def visit_text(self, node):
        if self.config.get("in_link"):
            node.content = node.content.upper()
        return node

    def visit_link(self, node):
        self.config["in_link"] = True
        self.generic_visit(node)
        self.config["in_link"] = False
        return node


doc = Tidy().transform(parser.parse("![x](a.png) see [the docs](https://example.com)\n"))
print(md.render(doc))
```

Output:

```markdown
 see [THE DOCS](https://example.com)
```

`TransformerChain(transformers)` runs a list of transformers in order and has `add_transformer()` and `remove_transformer()`. `TransformerRegistry` offers `register()`, `get()`, `create()`, `list_transformers()` and `create_chain(names, configs=None)`, but none of the shipped transformers register themselves, so you must register any you want to create by name.
