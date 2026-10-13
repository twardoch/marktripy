# Parsers

A parser takes a Markdown string and returns a `Document`. Two adapters ship with the package:

| Registry name | Class | Module | Built on |
|---|---|---|---|
| `markdown-it` | `MarkdownItParser` | `marktripy.parsers.markdown_it` | `markdown-it-py` |
| `mistletoe` | `MistletoeParser` | `marktripy.parsers.mistletoe_parser` | `mistletoe` |

Use `markdown-it` unless you have a reason not to. It is the adapter the test suite exercises most, and it is the only one that takes configuration. The `mistletoe` adapter drops several constructs; see [The mistletoe adapter](#the-mistletoe-adapter).

## Create a parser

Each adapter module registers itself with `ParserRegistry` when it is imported. Nothing is registered until then.

```python
from marktripy.core.parser import ParserRegistry
from marktripy.parsers import markdown_it, mistletoe_parser  # both register now

print(ParserRegistry.list_parsers())   # ['markdown-it', 'mistletoe']

parser = ParserRegistry.create("markdown-it", {"preset": "default"})
```

`ParserRegistry.create(name, config=None)` looks up the class and calls it with `config`. If the name is unknown, `ParserRegistry.get` raises `KeyError` and lists the names that are registered, for example `Parser 'mistletoe' not registered. Available: ['markdown-it']` when you forgot the import.

Constructing the class directly works the same way:

```python
from marktripy.parsers.markdown_it import MarkdownItParser

parser = MarkdownItParser({"preset": "default"})
```

## What `parse()` does

`parse(text)` runs three steps:

1. `preprocess(text)` converts `\r\n` and `\r` line endings to `\n` and adds a final newline if missing.
2. The backend parses the text, and the adapter converts the backend's tokens into `ASTNode` objects.
3. `postprocess(doc)` returns the document. The base implementation does not change it; subclasses can override it.

Any exception raised inside `parse()` is re-raised as `ParserError` with the message `Failed to parse Markdown: <original message>`. The original exception is available as `__cause__`. `ParserError` also has `line` and `column` attributes, but the shipped adapters do not set them.

`validate_markdown(text)` calls `parse()` and returns a list with the error message if parsing fails, or an empty list if it succeeds.

## The markdown-it adapter

`MarkdownItParser` accepts a configuration dictionary with these keys:

| Key | Default | Effect |
|---|---|---|
| `preset` | `"commonmark"` | `markdown-it-py` preset name: `"commonmark"`, `"default"` or `"zero"`. |
| `options` | `{}` | Options passed to `MarkdownIt(preset, options)`, for example `{"typographer": True}`. |
| `plugins` | `[]` | Plugin names to load from `mdit_py_plugins`: `front_matter`, `footnote`, `deflist`, `tasklists`, `attrs`. Unknown names are logged and skipped. |
| `disable` | `[]` | Rule names passed to `md.disable()`. |
| `enable` | `[]` | Rule names passed to `md.enable()`. |

The adapter always enables the `html_inline` and `html_block` rules unless `options["html"]` is `False`.

### Choose a preset

The preset decides which syntax is recognised. The `commonmark` default does **not** recognise tables or `~~strikethrough~~`. Use `"default"` for those:

```python
ParserRegistry.create("markdown-it").get_capabilities()["tables"]                         # False
ParserRegistry.create("markdown-it", {"preset": "default"}).get_capabilities()["tables"]  # True
```

### Token mapping

The adapter maps `markdown-it-py` tokens to nodes as follows:

| Token | Node |
|---|---|
| `heading_open` | `Heading(level=…)` from the tag (`h2` → 2) |
| `paragraph_open` | `Paragraph` |
| `blockquote_open` | `BlockQuote` |
| `hr` | `HorizontalRule` |
| `fence`, `code_block` | `CodeBlock(content, language=info)` |
| `bullet_list_open` / `ordered_list_open` | `List(ordered=…, start=…, tight=…)` |
| `list_item_open` | `ListItem` |
| `em_open`, `strong_open` | `Emphasis`, `Strong` |
| `s_open` | a plain `ASTNode(type="strikethrough")` |
| `link_open` | `Link(href, title)` |
| `image` | `Image(src, alt, title)` |
| `code_inline` | `InlineCode` |
| `text` | `Text` |
| `softbreak`, `hardbreak` | `Text("\n")` |
| `html_inline`, `html_block` | `Text` holding the raw HTML |
| `table_open`, `tr_open`, `th_open`/`td_open` | `Table`, `TableRow`, `TableCell(header=…, align=…)` |

Tokens not in this list are skipped. Two consequences:

- Raw HTML becomes ordinary text. `HTMLRenderer` escapes it, so `<b>x</b>` in the source becomes `&lt;b&gt;x&lt;/b&gt;` in the output.
- A hard line break (two trailing spaces) becomes the same `Text("\n")` as a soft break, so it renders as a plain newline.

### Plugins

Plugins add syntax to the tokenizer, but the adapter only converts the token types listed above. For example, with `{"plugins": ["front_matter"]}` the front matter block is recognised and then skipped, so it does not appear in the tree:

```python
p = ParserRegistry.create("markdown-it", {"plugins": ["front_matter"]})
[n.type for n in p.parse("---\ntitle: x\n---\n\n# H\n").walk()]
# ['document', 'heading', 'text']
```

## The mistletoe adapter

`MistletoeParser` takes no configuration keys. It calls `mistletoe.Document(text)` and converts headings, paragraphs, lists, code blocks, quotes, tables, emphasis, strong, inline code and links.

With `mistletoe` 1.6 the adapter has these gaps:

- Fenced code blocks (```` ``` ````) and `~~strikethrough~~` are dropped from the tree with a logged warning. Indented code blocks are converted.
- Any image makes `parse()` fail with `ParserError: Failed to parse Markdown: 'Image' object has no attribute 'target'`.
- Table column alignment is copied as `mistletoe`'s numeric code instead of `"left"`, `"center"` or `"right"`. A right-aligned column, for example, produces `align="1"` in HTML.

Prefer the `markdown-it` adapter for real documents until these are fixed.

## Capabilities

`get_capabilities()` returns a dictionary of feature flags: `tables`, `strikethrough`, `task_lists`, `footnotes`, `definition_lists`, `math`, `smart_quotes` and `custom_extensions`.

For `MarkdownItParser` the values are computed from the active `markdown-it-py` rules, so they change with the preset and plugins. For `MistletoeParser` they are fixed values and do not reflect the gaps listed above.

## Write your own adapter

Subclass `Parser`, implement `parse()` and `get_capabilities()`, and register the class:

```python
from marktripy.core.ast import Document, Paragraph, Text
from marktripy.core.parser import Parser, ParserRegistry


class PlainTextParser(Parser):
    """Treat every blank-line-separated block as a paragraph."""

    def parse(self, text: str) -> Document:
        doc = Document()
        for block in self.preprocess(text).split("\n\n"):
            if block.strip():
                para = Paragraph()
                para.add_child(Text(block.strip()))
                doc.add_child(para)
        return self.postprocess(doc)

    def get_capabilities(self) -> dict[str, bool]:
        return {"tables": False, "custom_extensions": False}


ParserRegistry.register("plain", PlainTextParser)
```

`ParserRegistry.register` raises `TypeError` if the class is not a `Parser` subclass. Registering an existing name replaces the earlier class.
