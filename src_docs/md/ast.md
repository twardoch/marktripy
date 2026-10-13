# The AST

All parsers produce, and all transformers and renderers consume, the same tree of `ASTNode` objects defined in `marktripy/core/ast.py`.

## The base class

`ASTNode` is a dataclass with five fields:

| Field | Type | Default | Meaning |
|---|---|---|---|
| `type` | `str` | required | Node kind, such as `"heading"` or `"text"`. An empty string raises `ValueError`. |
| `children` | `list[ASTNode]` | `[]` | Child nodes, in document order |
| `attrs` | `dict[str, Any]` | `{}` | Attributes. `HTMLRenderer` writes most of them as HTML attributes. |
| `content` | `str \| None` | `None` | Text for leaf nodes (`text`, `inline_code`, `code_block`) |
| `meta` | `dict[str, Any]` | `{}` | Free space for parser- or tool-specific data. Nothing in the package reads it. |

The `type` string drives dispatch everywhere: renderers call `render_<type>`, transformers call `visit_<type>`, and the validator calls `_validate_<type>`. A node you create with `ASTNode(type="callout")` is therefore a valid node; a renderer only needs a `render_callout` method to output it.

## Tree methods

| Method | What it does |
|---|---|
| `add_child(child)` | Appends `child` to `children`. |
| `remove_child(child)` | Removes `child`. Raises `ValueError` if it is not a child. |
| `replace_child(old, new)` | Puts `new` in the position of `old`. Raises `ValueError` if `old` is not a child. |
| `get_attr(name, default=None)` | Reads `attrs[name]`. |
| `set_attr(name, value)` | Writes `attrs[name]`. |
| `walk()` | Returns a list of this node and all descendants, depth first, parent before children. |
| `find_all(node_type)` | Returns every node in `walk()` whose `type` equals `node_type`. |
| `clone()` | Returns a deep copy of the subtree. `attrs` and `meta` are copied one level deep. |

Nodes do not store a reference to their parent. To find a parent, search from the root: `next(n for n in root.walk() if child in n.children)`.

`walk()` builds the full list before returning it, so it is safe to change node attributes while you loop over it. If you add or remove children during the loop, the loop still visits the nodes that existed when `walk()` was called.

## Node classes

Each concrete class fixes `type` and adds typed fields. The constructors also copy some fields into `attrs` so that `HTMLRenderer` can write them.

| Class | `type` | Extra fields (constructor arguments) | Copied into `attrs` |
|---|---|---|---|
| `Document` | `document` | — | — |
| `Heading` | `heading` | `level=1` (must be 1–6, else `ValueError`) | — |
| `Paragraph` | `paragraph` | — | — |
| `Text` | `text` | `content` (required) | — |
| `Emphasis` | `emphasis` | — | — |
| `Strong` | `strong` | — | — |
| `Link` | `link` | `href=""`, `title=None` | `href`, and `title` if set |
| `Image` | `image` | `src=""`, `alt=""`, `title=None` | `src`, `alt`, and `title` if set |
| `CodeBlock` | `code_block` | `content` (required), `language=None` | `language` if set |
| `InlineCode` | `inline_code` | `content` (required) | — |
| `List` | `list` | `ordered=False`, `start=None`, `tight=True` | `start` if it is not `None` and not `1` |
| `ListItem` | `list_item` | — | — |
| `BlockQuote` | `blockquote` | — | — |
| `HorizontalRule` | `horizontal_rule` | — | — |
| `Table` | `table` | — | — |
| `TableRow` | `table_row` | — | — |
| `TableCell` | `table_cell` | `header=False`, `align=None` | `align` if set |

All constructors also accept the base-class keyword arguments `children`, `attrs` and `meta`, and `content` where it is not already required.

Extensions add two more node types, `strikethrough` and `keyboard_key`, and the task-list attributes `task` and `checked` on `list_item` nodes. See [Extensions](extensions.md).

!!! note "Typed fields and `attrs` are separate"
    `Link.href` and `attrs["href"]` start out equal, but changing one does not update the other. `HTMLRenderer.render_link` reads `node.href`; `MarkdownRenderer.render_link` also reads `node.href`. Change the field, not the attribute.

## Build a tree by hand

You do not need a parser to create a document:

```python
from marktripy.core.ast import CodeBlock, Document, Heading, Paragraph, Strong, Text
from marktripy.renderers.markdown import MarkdownRenderer

doc = Document()

heading = Heading(level=2)
heading.add_child(Text("Install"))
doc.add_child(heading)

para = Paragraph()
para.add_child(Text("Run "))
bold = Strong()
bold.add_child(Text("uv"))
para.add_child(bold)
doc.add_child(para)

doc.add_child(CodeBlock("uv add marktripy\n", language="bash"))

print(MarkdownRenderer().render(doc))
```

Output:

````markdown
## Install

Run **uv**

```bash
uv add marktripy
```
````

## Common edits

Lower every heading by one level, stopping at level 6:

```python
for h in doc.find_all("heading"):
    h.level = min(h.level + 1, 6)
```

Replace every link target that starts with `http://`:

```python
for link in doc.find_all("link"):
    if link.href.startswith("http://"):
        link.href = "https://" + link.href[len("http://"):]
```

Collect the plain text of a node with `extract_text` from `marktripy.utils.slugify`:

```python
from marktripy.utils.slugify import extract_text

titles = [extract_text(h) for h in doc.find_all("heading")]
```

Remove all images:

```python
for parent in doc.walk():
    parent.children = [c for c in parent.children if c.type != "image"]
```

Make an independent copy before a destructive change:

```python
backup = doc.clone()
```
