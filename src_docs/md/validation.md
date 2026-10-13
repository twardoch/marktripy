# Validation and utilities

## Validate a tree

`marktripy.core.validator` checks that a tree has a sensible structure. It is useful after you build or edit a tree by hand, before you render it.

```python
from marktripy.core.ast import Document, List, Paragraph, Text
from marktripy.core.validator import validate_ast

doc = Document()
doc.add_child(Text("loose"))          # inline node directly under the document
bad_list = List()
bad_list.add_child(Paragraph())       # list that contains a paragraph
doc.add_child(bad_list)

for error in validate_ast(doc):
    print(error)
```

Output:

```text
Document contains inline element at text node
List contains non-list-item: paragraph at paragraph node
```

Each error is a `ValidationError` (a subclass of `Exception`). Its message ends with `at <type> node`, and its `node` attribute holds the node that failed.

### Entry points

| Call | Result |
|---|---|
| `validate_ast(ast, strict=False)` | Returns a list of `ValidationError`; empty if the tree is valid. |
| `validate_ast_strict(ast)` | Runs strict validation and raises the first error. |
| `ASTValidator(strict=False).validate(ast)` | Same as `validate_ast`. The errors are also kept in `validator.errors`. |
| `ASTValidator(strict=…).validate_strict(ast)` | Validates and raises the first error, if any. Despite the name, it uses the validator's own `strict` setting. |

### Rules

The validator visits every node and calls `_validate_<type>` for it.

| Node type | Always checked | Checked only with `strict=True` |
|---|---|---|
| `document` | No direct `text`, `emphasis`, `strong` or `inline_code` children | — |
| `heading` | Level is 1–6; has children or content | — |
| `list` | Only `list_item` children; ordered `start` is not negative | — |
| `list_item` | — | Not empty |
| `link` | `href` is not empty | Has text |
| `image` | `src` is not empty; has no children | — |
| `table` | Only `table_row` children; all rows have the same number of cells | — |
| `table_row` | Only `table_cell` children | — |
| `blockquote` | — | Not empty |
| any other type | — | Logs a warning (not an error) |

Example: a link with an empty target, as parsed from `[x]()`:

```python
from marktripy.core.parser import ParserRegistry
from marktripy.parsers import markdown_it

doc = ParserRegistry.create("markdown-it").parse("# ok\n\n[x]()\n")
print(validate_ast(doc))
# [ValidationError('Link has no href at link node')]
```

## Slugs and IDs

`marktripy.utils.slugify` contains the text helpers the transformers use. You can call them directly.

### `slugify(text, lowercase=True, separator="-", max_length=None, allowed_chars=None)`

Converts text to a URL-friendly slug in five steps: NFKD-normalise and drop non-ASCII, optionally lower-case, remove characters other than letters, digits, whitespace, hyphens and `allowed_chars`, collapse whitespace and hyphen runs into `separator`, strip `separator` from the ends. If `max_length` is set, the result is cut to that length and trailing separators are removed.

```python
from marktripy.utils.slugify import slugify

slugify("Hello, World! Café")             # 'hello-world-cafe'
slugify("Hello World", separator="_")     # 'hello_world'
slugify("v1.2 notes", allowed_chars=".")  # 'v1.2-notes'
```

### `generate_id(text, existing_ids=None)`

Slugifies `text` and makes it unique against the set `existing_ids` by appending `-1`, `-2`, …. An empty slug becomes `section`. The function does not add the result to the set.

```python
from marktripy.utils.slugify import generate_id

generate_id("Intro", {"intro"})   # 'intro-1'
generate_id("!!!")                # 'section'
```

### `IDGenerator(prefix="", separator="-")`

A stateful wrapper around `generate_id`. `generate(text)` prepends `prefix` + `separator` when a prefix is set, returns a unique ID and remembers it in `used_ids`. `has_id(value)` checks whether an ID was issued; `reset()` forgets them all.

### `extract_text(node)`

Returns the plain text of a node: its `content` if set, otherwise the concatenated text of its children. Formatting is dropped, so `**bold** text` gives `bold text`.
