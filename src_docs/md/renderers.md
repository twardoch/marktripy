# Renderers

A renderer turns a `Document` into a string. Two renderers ship with the package and register themselves when their module is imported:

| Registry name | Class | Module | Output |
|---|---|---|---|
| `markdown` | `MarkdownRenderer` | `marktripy.renderers.markdown` | Markdown |
| `html` | `HTMLRenderer` | `marktripy.renderers.html` | HTML fragment (no `<html>` or `<body>`) |

```python
from marktripy.renderers.base import RendererRegistry
from marktripy.renderers import html, markdown  # registers "html" and "markdown"

renderer = RendererRegistry.create("markdown", {"bullet_char": "*"})
```

Constructing the class directly is equivalent: `MarkdownRenderer({"bullet_char": "*"})`.

## How rendering works

`render(ast)` resets the render context and calls `render_node(ast)`. `render_node` looks up a method named `render_<node.type>` on the renderer and calls it. Each method renders its children by calling `render_node` again, so the whole tree is visited depth first.

If no method matches, `render_unknown` runs:

- `MarkdownRenderer` logs a warning and outputs nothing for that node.
- `HTMLRenderer` logs a warning and outputs `<!-- Unknown node type: <type> -->`.

This lookup is also how extensions add output for new node types: they attach a `render_<type>` function to the renderer instance. You can do the same:

```python
from marktripy.core.ast import ASTNode, Document
from marktripy.renderers.html import HTMLRenderer

html = HTMLRenderer()
html.render_callout = lambda node: f'<aside>{html.render_children(node)}</aside>\n'

doc = Document()
doc.add_child(ASTNode(type="callout", children=[]))
print(html.render(doc))   # <aside></aside>
```

## MarkdownRenderer

### Options

| Key | Default | Effect |
|---|---|---|
| `heading_style` | `"atx"` | `"setext"` writes level 1 and 2 headings with `===` / `---` underlines. Levels 3–6 always use `#`. |
| `emphasis_char` | `"*"` | Delimiter for `emphasis` nodes, for example `"_"`. |
| `strong_char` | `"**"` | Delimiter for `strong` nodes, for example `"__"`. |
| `bullet_char` | `"-"` | Marker for unordered list items. |
| `code_fence` | `` "`" `` | Character repeated three times to fence code blocks. `"~"` gives `~~~`. |
| `line_width` | `0` | If greater than 0, paragraph text is re-wrapped at this width. `0` means no wrapping. |
| `preserve_format` | `False` | Stored on the renderer but not used by any method. |
| `indent` | `"  "` | Used by `get_indent()`. List rendering uses a fixed three-space continuation indent instead. |

Example with non-default options:

```python
from marktripy.core.parser import ParserRegistry
from marktripy.parsers import markdown_it
from marktripy.renderers.markdown import MarkdownRenderer

doc = ParserRegistry.create("markdown-it").parse("# Title\n\n*it* and\n\n- a\n")
r = MarkdownRenderer({"heading_style": "setext", "emphasis_char": "_", "bullet_char": "*"})
print(r.render(doc))
```

Output:

```markdown
Title
=====

_it_ and

* a
```

### Output rules

- Blocks in the document are separated by one blank line. The output always ends with exactly one newline.
- Ordered lists are numbered from `List.start` (or 1) and counted up, so `3. x` / `4. y` round-trips.
- Code blocks use a fence of three `code_fence` characters, or four if the content already contains three. The language follows the opening fence.
- Inline code uses enough backticks to enclose any backticks in the content.
- A `Link` with a `reference_id` attribute is written as `[text][id]`. Otherwise it is written inline, with the title in quotes if set.
- Tables are written with padded columns and a separator row that shows alignment (`:--`, `--:`, `:-:`). The first row is treated as the header if all its cells have `header=True`.
- `HorizontalRule` is always written as `---`.

### Escaping

`render_text` escapes these characters with a backslash in every `text` node: `` \ * _ ` [ ] ( ) # + - ! | { } ``. It does this without looking at context, so plain prose picks up escapes that a person would not write:

```python
doc = ParserRegistry.create("markdown-it").parse("Use the well-known foo_bar (see #1).\n")
print(MarkdownRenderer().render(doc))
# Use the well\-known foo\_bar \(see \#1\).
```

The escaped Markdown renders to the same text, but it is not byte-for-byte what you parsed. Text inside `inline_code` and `code_block` nodes is not escaped.

## HTMLRenderer

### Options

The option names follow `markdown-it` conventions.

| Key | Default | Effect |
|---|---|---|
| `xhtml` | `False` | Writes `<hr />` and `<img … />` instead of `<hr>` and `<img …>`. |
| `breaks` | `False` | Replaces each newline inside a text node with `<br>` plus a newline. |
| `langPrefix` | `"language-"` | Prefix for the `class` added to code blocks with a language. |
| `typographer` | `False` | Replaces `--` with an em dash (`—`) and `...` with an ellipsis (`…`) in text nodes. Quote replacement is not implemented. |
| `quotes` | `'""' + "''"` | Stored but unused, because quote replacement is not implemented. |
| `linkify` | `False` | Stored but unused. |

Example:

```python
from marktripy.renderers.html import HTMLRenderer

doc = ParserRegistry.create("markdown-it").parse("a -- b...\nline2\n\n---\n")
print(HTMLRenderer({"xhtml": True, "typographer": True, "breaks": True}).render(doc))
```

Output:

```html
<p>a — b…<br>
line2</p>
<hr />
```

### Output rules

- Text, code, link `href`/`title` and image `src`/`alt`/`title` are escaped with `html.escape(…, quote=True)`.
- Every entry in a node's `attrs` becomes an HTML attribute. `True` writes the bare attribute name; `False` and `None` are skipped; other values are converted to strings and escaped. Heading IDs therefore appear as `<h2 id="setup">`.
- Because `CodeBlock` stores its language in `attrs` too, a fenced block produces both a `language` attribute and a class: `<pre><code language="python" class="language-python">`.
- Ordered lists with a start other than 1 get a `start` attribute.
- In tight lists, a list item that renders as a single `<p>…</p>` has the paragraph tags removed.
- Table cells with an alignment get both `align="…"` (from `attrs`) and `style="text-align: …;"`.
- Empty paragraphs produce no output.

## Write your own renderer

Subclass `Renderer` and implement `render()` and `render_node()`. The base class provides `render_children()`, `escape()` (returns the text unchanged) and `get_indent()`.

```python
from marktripy.core.ast import ASTNode, Document
from marktripy.renderers.base import Renderer, RendererRegistry


class PlainTextRenderer(Renderer):
    """Output only the text content, one block per line."""

    def render(self, ast: Document) -> str:
        return "\n".join(self.render_node(child) for child in ast.children) + "\n"

    def render_node(self, node: ASTNode) -> str:
        if node.content is not None:
            return node.content
        return self.render_children(node)


RendererRegistry.register("plain", PlainTextRenderer)
```

`RenderContext` (in `marktripy.renderers.base`) holds per-render state that the shipped renderers use: `list_depth`, `tight_list`, `in_table`, `in_code_block`, plus `set_data()` / `get_data()` for your own values. Both shipped renderers create a fresh context at the start of every `render()` call and store it in `self.context`.
