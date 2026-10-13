# API reference

This page lists every public module, class and function, with the page that explains it. The package has no top-level re-exports apart from `__version__`; import names from the module shown.

## `marktripy`

| Name | Kind | Notes |
|---|---|---|
| `__version__` | `str` | Read from `marktripy/_version.py`, which the build writes. Falls back to `"0.0.0"` in an unbuilt source tree. |
| `__author__` | `str` | `"Adam Twardoch"` |

Importing `marktripy` also calls `loguru.logger.disable("marktripy")`. See [Installation](installation.md#turn-on-logging).

## `marktripy.core`

`marktripy.core` re-exports `ASTNode` and `Parser`.

### `marktripy.core.ast`

See [The AST](ast.md).

| Name | Kind |
|---|---|
| `ASTNode(type, children=[], attrs={}, content=None, meta={})` | Base dataclass. Methods: `add_child`, `remove_child`, `replace_child`, `get_attr`, `set_attr`, `walk`, `find_all`, `clone`. |
| `Document`, `Paragraph`, `Emphasis`, `Strong`, `ListItem`, `BlockQuote`, `HorizontalRule`, `Table`, `TableRow` | Node classes without extra fields |
| `Heading(level=1)` | Heading; `level` 1–6 |
| `Text(content)`, `InlineCode(content)` | Leaf nodes |
| `CodeBlock(content, language=None)` | Code block |
| `Link(href="", title=None)` | Link |
| `Image(src="", alt="", title=None)` | Image |
| `List(ordered=False, start=None, tight=True)` | List |
| `TableCell(header=False, align=None)` | Table cell |

### `marktripy.core.parser`

See [Parsers](parsers.md).

| Name | Kind |
|---|---|
| `Parser(config=None)` | Abstract base. Abstract: `parse(text)`, `get_capabilities()`. Provided: `preprocess(text)`, `postprocess(ast)`, `validate_markdown(text)`. |
| `ParserError(message, line=None, column=None)` | Exception raised by `parse()` |
| `ParserRegistry` | Class methods: `register(name, cls)`, `get(name)`, `create(name, config=None)`, `list_parsers()` |

### `marktripy.core.validator`

See [Validation and utilities](validation.md).

| Name | Kind |
|---|---|
| `ASTValidator(strict=False)` | Methods: `validate(ast)` → list of errors, `validate_strict(ast)` raises the first |
| `ValidationError(message, node=None)` | Exception; `node` attribute |
| `validate_ast(ast, strict=False)` | Function → list of `ValidationError` |
| `validate_ast_strict(ast)` | Function; raises the first error |

## `marktripy.parsers`

| Module | Class | Registry name |
|---|---|---|
| `marktripy.parsers.markdown_it` | `MarkdownItParser(config=None)` | `markdown-it` |
| `marktripy.parsers.mistletoe_parser` | `MistletoeParser(config=None)` | `mistletoe` |

Configuration keys for `MarkdownItParser`: `preset`, `options`, `plugins`, `disable`, `enable`. See [Parsers](parsers.md#the-markdown-it-adapter).

## `marktripy.renderers`

See [Renderers](renderers.md).

| Module | Names |
|---|---|
| `marktripy.renderers.base` | `Renderer(config=None)` (abstract: `render`, `render_node`; provided: `render_children`, `escape`, `get_indent`), `RendererError`, `RenderContext`, `RendererRegistry` (`register`, `get`, `create`, `list_renderers`) |
| `marktripy.renderers.markdown` | `MarkdownRenderer(config=None)`, registry name `markdown` |
| `marktripy.renderers.html` | `HTMLRenderer(config=None)`, registry name `html` |

## `marktripy.transformers`

See [Transformers](transformers.md).

| Module | Names |
|---|---|
| `marktripy.transformers.base` | `Transformer(config=None)` (abstract: `get_description`; provided: `transform`, `visit`, `generic_visit`), `TransformerChain(transformers)`, `TransformerRegistry` (`register`, `get`, `create`, `list_transformers`, `create_chain`) |
| `marktripy.transformers.heading` | `HeadingLevelTransformer(config=None)`, `HeadingShifter(shift)`, `HeadingNormalizer()`, `increase_heading_levels(ast, amount=1)`, `decrease_heading_levels(ast, amount=1)`, `normalize_headings(ast)` |
| `marktripy.transformers.id_generator` | `IDGeneratorTransformer(config=None)`, `HeadingIDGenerator(prefix="", overwrite=False)`, `TableIDGenerator(prefix="table", overwrite=False)`, `add_heading_ids(ast, prefix="", overwrite=False)`, `add_ids_to_elements(ast, elements, prefix="", overwrite=False)` |
| `marktripy.transformers.toc` | `TOCGenerator(config=None)` (adds `get_toc()`), `generate_toc(ast, max_level=3, insert=True)`, `extract_toc(ast, max_level=3)` |
| `marktripy.transformers.link_reference` | `LinkReferenceTransformer(config=None)`, `LinkCollector()` (adds `get_links()`), `convert_to_reference_links(ast, style="numeric", dedup=True)`, `collect_links(ast)` |

## `marktripy.extensions`

See [Extensions](extensions.md).

| Module | Names |
|---|---|
| `marktripy.extensions.base` | `Extension(config=None)` (abstract: `get_name`, `get_description`; hooks: `get_dependencies`, `register_inline_rule`, `register_block_rule`, `transform_ast`, `register_html_renderer`, `register_markdown_renderer`, `setup`, `teardown`), `ExtensionManager()` |
| `marktripy.extensions.strikethrough` | `StrikethroughExtension`, node class `Strikethrough()` |
| `marktripy.extensions.tasklist` | `TaskListExtension` |
| `marktripy.extensions.kbd` | `KbdExtension`, node class `KeyboardKey(key)` |
| `marktripy.extensions.gfm` | `GFMExtension` |

## `marktripy.utils.slugify`

See [Validation and utilities](validation.md#slugs-and-ids).

| Name | Kind |
|---|---|
| `slugify(text, lowercase=True, separator="-", max_length=None, allowed_chars=None)` | Function → `str` |
| `generate_id(text, existing_ids=None)` | Function → `str` |
| `extract_text(node)` | Function → `str` |
| `IDGenerator(prefix="", separator="-")` | Class: `generate(text)`, `reset()`, `has_id(id_value)`, attribute `used_ids` |
