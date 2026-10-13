# Extensions

An extension bundles three optional pieces of behaviour for one feature:

1. an **AST transformation** that runs after parsing (`transform_ast`),
2. a **render method** for HTML (`register_html_renderer`),
3. a **render method** for Markdown (`register_markdown_renderer`).

The shipped extensions do all their work in these hooks. They do not add tokenizer rules: the `register_inline_rule` and `register_block_rule` hooks exist on the base class but the shipped extensions only log a message there.

| Extension | Module | Name | Syntax |
|---|---|---|---|
| `StrikethroughExtension` | `marktripy.extensions.strikethrough` | `strikethrough` | `~~text~~` |
| `TaskListExtension` | `marktripy.extensions.tasklist` | `tasklist` | `- [ ] item`, `- [x] item` |
| `KbdExtension` | `marktripy.extensions.kbd` | `kbd` | `++key++` |
| `GFMExtension` | `marktripy.extensions.gfm` | `gfm` | Strikethrough plus task lists |

## Use extensions

`ExtensionManager` (in `marktripy.extensions.base`) holds a set of extensions and applies them in registration order.

Prerequisites: a parser and the renderers you plan to use.

1. Create the parser. Use the `default` preset if you need strikethrough or tables:

    ```python
    from marktripy.core.parser import ParserRegistry
    from marktripy.parsers import markdown_it

    parser = ParserRegistry.create("markdown-it", {"preset": "default"})
    ```

2. Register the extensions:

    ```python
    from marktripy.extensions.base import ExtensionManager
    from marktripy.extensions.gfm import GFMExtension
    from marktripy.extensions.kbd import KbdExtension

    manager = ExtensionManager()
    manager.register(GFMExtension())
    manager.register(KbdExtension())
    ```

3. Attach the render methods to each renderer instance. The second argument is `"html"` or `"markdown"`:

    ```python
    from marktripy.renderers.html import HTMLRenderer
    from marktripy.renderers.markdown import MarkdownRenderer

    html = HTMLRenderer()
    md = MarkdownRenderer()
    manager.apply_renderer_extensions(html, "html")
    manager.apply_renderer_extensions(md, "markdown")
    ```

4. Parse, then run the AST transformations, then render:

    ```python
    doc = parser.parse("Press ++Enter++. ~~old~~ new.\n\n- [ ] todo\n- [x] done\n")
    doc = manager.apply_ast_transformations(doc)

    print(html.render(doc))
    print(md.render(doc))
    ```

The HTML output:

```html
<p>Press <kbd>Enter</kbd>. <del>old</del> new.</p>
<ul>
<li><input type="checkbox" disabled> todo</li><li><input type="checkbox" disabled checked> done</li></ul>
```

The Markdown output round-trips the extension syntax:

```markdown
Press ++Enter++. ~~old~~ new.

- [ ] todo
- [x] done
```

If you skip step 3, the renderer has no method for the new node types: `HTMLRenderer` writes `<!-- Unknown node type: keyboard_key -->` and `MarkdownRenderer` drops the node. If you skip step 4, the `++key++` text and the `[ ]` prefixes stay as plain text.

### Manager methods

| Method | What it does |
|---|---|
| `register(extension)` | Adds the extension and calls its `setup()`. Raises `ValueError` if the name is taken or a dependency from `get_dependencies()` is not registered yet. |
| `unregister(name)` | Calls `teardown()` and removes the extension. Raises `KeyError` if unknown, `ValueError` if another extension depends on it. |
| `get(name)` | Returns the registered extension. Raises `KeyError` if unknown. |
| `list_extensions()` | Returns the names in load order. |
| `apply_parser_extensions(parser)` | Calls `register_inline_rule` and `register_block_rule` on every extension. |
| `apply_ast_transformations(ast)` | Calls `transform_ast` on every extension, feeding each result to the next, and returns the final tree. |
| `apply_renderer_extensions(renderer, format="html")` | Calls `register_html_renderer` or `register_markdown_renderer` on every extension. |

## Strikethrough

The `markdown-it` adapter turns `~~text~~` into a generic node of type `strikethrough` when the preset supports it (`default`, not `commonmark`). `StrikethroughExtension.transform_ast` replaces each generic node with a `Strikethrough` instance (same type string, same children). The render methods output `<del>…</del>` and `~~…~~`.

## Task lists

`TaskListExtension.transform_ast` looks at the first text of each list item. If it matches `[ ]`, `[x]` or `[X]` followed by whitespace, the extension:

- sets `attrs["task"] = True` and `attrs["checked"]` to `True` or `False`,
- removes the `[ ]` / `[x]` prefix from the text.

The HTML method writes `<li><input type="checkbox" disabled> …</li>` (adding `checked` for done items). The Markdown method writes `[ ] …` or `[x] …` after the list marker. Items without the prefix are rendered by the renderer's original `render_list_item`.

You do not need the `tasklists` parser plugin for this; the extension works on the plain list text.

## Keyboard keys

`KbdExtension.transform_ast` searches every `text` node for the pattern `++…++` and splits the node into text and `KeyboardKey` nodes (type `keyboard_key`). The key text is in `node.key`.

HTML output is `<kbd>key</kbd>`. Markdown output is `++key++`.

The pattern does not allow `+` inside the key, so `++Ctrl+C++` is left as text. Write key combinations as separate keys: `++Ctrl++ + ++C++` gives `<kbd>Ctrl</kbd> + <kbd>C</kbd>`.

## GFM bundle

`GFMExtension` creates a `StrikethroughExtension` and a `TaskListExtension` internally and forwards every hook to both. Register it instead of the two separate extensions; registering both would apply them twice. Tables are not part of the bundle because the parser handles them (with the `default` preset).

## Write your own extension

Subclass `Extension`, implement `get_name()` and `get_description()`, and override the hooks you need. This extension turns `==text==` inside text nodes into a `mark` node:

```python
import re

from marktripy.core.ast import ASTNode, Text
from marktripy.extensions.base import Extension

PATTERN = re.compile(r"==([^=]+)==")


class MarkExtension(Extension):
    def get_name(self) -> str:
        return "mark"

    def get_description(self) -> str:
        return "Highlight text written as ==text=="

    def transform_ast(self, ast: ASTNode) -> ASTNode:
        for node in ast.walk():
            new_children = []
            for child in node.children:
                if isinstance(child, Text) and child.content and PATTERN.search(child.content):
                    pos = 0
                    for m in PATTERN.finditer(child.content):
                        if m.start() > pos:
                            new_children.append(Text(child.content[pos:m.start()]))
                        new_children.append(ASTNode(type="mark", children=[Text(m.group(1))]))
                        pos = m.end()
                    if pos < len(child.content):
                        new_children.append(Text(child.content[pos:]))
                else:
                    new_children.append(child)
            node.children = new_children
        return ast

    def register_html_renderer(self, renderer) -> None:
        renderer.render_mark = lambda node: f"<mark>{renderer.render_children(node)}</mark>"

    def register_markdown_renderer(self, renderer) -> None:
        renderer.render_mark = lambda node: f"=={renderer.render_children(node)}=="
```

Points to follow:

- Attach render methods to the renderer **instance** you received, as `render_<type>`. The renderers look methods up by name at render time.
- To change how an existing node type renders, keep a reference to the old method and call it for the cases you do not handle. `TaskListExtension` does this with `render_list_item`.
- Return a list of names from `get_dependencies()` if your extension needs another one registered first.
