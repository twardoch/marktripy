# Known limitations

These behaviours were confirmed by running the current code. Each entry says what happens and what to do instead.

## `ImportError: cannot import name 'parse_markdown'`

The README examples use `parse_markdown`, `render_markdown`, `markdown_to_html`, `create_extension` and a `Parser(extensions=…)` constructor. None of these exist. Use the module-level classes:

| README name | Use instead |
|---|---|
| `parse_markdown(text)` | `ParserRegistry.create("markdown-it").parse(text)` |
| `render_markdown(ast)` | `MarkdownRenderer().render(ast)` |
| `markdown_to_html(text)` | `HTMLRenderer().render(ParserRegistry.create("markdown-it").parse(text))` |
| `create_extension(…)` | Subclass `Extension`; see [Extensions](extensions.md#write-your-own-extension) |

## No command-line tool

The README shows `marktripy convert`, `marktripy transform` and `marktripy validate`. There is no CLI module, and the package installs no `marktripy` command.

## `Parser 'mistletoe' not registered`

`ParserRegistry` only knows a parser after its module is imported. Add `from marktripy.parsers import mistletoe_parser` (or `markdown_it`) before calling `ParserRegistry.create`. The same applies to `RendererRegistry` and the modules in `marktripy.renderers`.

## Tables are not recognised

The `markdown-it` adapter uses the `commonmark` preset by default, which has no table syntax. Pass `{"preset": "default"}`.

## Table body rows end up outside the table

With the `markdown-it` adapter, only the header row is placed inside the `Table` node. The body rows are added as siblings after the table. As a result:

- `MarkdownRenderer` writes the header and separator but no body rows.
- `HTMLRenderer` writes the body rows as bare `<tr>` elements after `</table>`.

The `mistletoe` adapter builds tables correctly (header and body inside `Table`), but has the other gaps listed below.

## `mistletoe` adapter gaps

- Fenced code blocks and strikethrough are dropped.
- Any image raises `ParserError: Failed to parse Markdown: 'Image' object has no attribute 'target'`.
- Column alignment is stored as `mistletoe`'s numeric code, giving HTML such as `align="1"`.

## Markdown output contains extra backslashes

`MarkdownRenderer` escapes `` \ * _ ` [ ] ( ) # + - ! | { } `` in every text node regardless of context. `well-known foo_bar (see #1)` becomes `well\-known foo\_bar \(see \#1\)`. The rendered result reads the same, but diffs against the source will show changes. See [Renderers](renderers.md#escaping).

## The `[[TOC]]` marker is not replaced

`TOCGenerator` is meant to replace a paragraph containing only the marker with the TOC. The parent lookup it uses never finds the paragraph, so the TOC is always inserted at the default position and the marker paragraph stays (escaped as `\[\[TOC\]\]` in Markdown output). Remove the marker paragraph yourself before or after running the generator.

## Reference definitions are escaped

`LinkReferenceTransformer` appends definitions such as `[1]: https://python.org` as text. `MarkdownRenderer` escapes them to `\[1\]: https://python.org`, which is not a valid definition, so the `[text][1]` links in the output do not resolve.

## Hard line breaks become soft

The `markdown-it` adapter converts both soft and hard breaks into `Text("\n")`. A line ending in two spaces loses its hard break in both Markdown and HTML output.

## Raw HTML is escaped in HTML output

Inline and block HTML in the source become `Text` nodes. `HTMLRenderer` escapes them, so `<b>x</b>` appears as literal text `&lt;b&gt;x&lt;/b&gt;`.

## Code blocks carry a `language` attribute in HTML

`CodeBlock` copies its language into `attrs`, and `HTMLRenderer` writes all attributes, so the output is `<code language="python" class="language-python">`. Remove it before rendering if you need clean HTML:

```python
for block in doc.find_all("code_block"):
    block.attrs.pop("language", None)
```

## `++Ctrl+C++` is not a keyboard key

`KbdExtension` does not allow `+` inside a key. Write `++Ctrl++ + ++C++`.

## Ignored configuration keys

These keys are read and stored but have no effect: `MarkdownRenderer` `preserve_format`; `HTMLRenderer` `linkify` and `quotes`; `TOCGenerator` `indent_size` and (because of the issue above) `marker`. Misspelt keys are ignored without an error.
