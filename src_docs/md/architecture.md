# Architecture

## Source layout

```text
src/marktripy/
├── __init__.py              # __version__, disables loguru output for the package
├── core/
│   ├── ast.py               # ASTNode and the concrete node classes
│   ├── parser.py            # Parser base class, ParserError, ParserRegistry
│   └── validator.py         # ASTValidator, ValidationError, validate_ast*
├── parsers/
│   ├── markdown_it.py       # MarkdownItParser  -> registry name "markdown-it"
│   └── mistletoe_parser.py  # MistletoeParser   -> registry name "mistletoe"
├── renderers/
│   ├── base.py              # Renderer, RenderContext, RendererRegistry
│   ├── markdown.py          # MarkdownRenderer  -> registry name "markdown"
│   └── html.py              # HTMLRenderer      -> registry name "html"
├── transformers/
│   ├── base.py              # Transformer (visitor), TransformerChain, TransformerRegistry
│   ├── heading.py           # heading level changes
│   ├── id_generator.py      # unique IDs for headings and other nodes
│   ├── toc.py               # table of contents
│   └── link_reference.py    # reference-style links, link collection
├── extensions/
│   ├── base.py              # Extension, ExtensionManager
│   ├── strikethrough.py     # ~~text~~
│   ├── tasklist.py          # - [ ] / - [x]
│   ├── kbd.py               # ++key++
│   └── gfm.py               # strikethrough + task lists
└── utils/
    └── slugify.py           # slugify, generate_id, extract_text, IDGenerator
```

## Data flow

```text
Markdown text
   │  Parser.preprocess()        normalise line endings, add final newline
   ▼
backend tokens  (markdown-it-py tokens or mistletoe tokens)
   │  adapter conversion         one ASTNode per supported token
   ▼
Document (ASTNode tree)
   │  Parser.postprocess()
   │  ExtensionManager.apply_ast_transformations()   optional
   │  Transformer.transform() / TransformerChain     optional
   │  direct edits                                   optional
   ▼
Document (changed)
   │  Renderer.render()          dispatch on node.type
   ▼
Markdown or HTML text
```

The tree is the only thing that passes between stages. A parser does not know which renderer will be used, and a renderer does not know which parser built the tree.

## Design decisions

**One node model for every backend.** Both parser adapters convert their backend's tokens into the same `ASTNode` classes. Transformers, extensions, the validator and renderers are written once against those classes. The cost is that anything an adapter does not convert is lost; see [Known limitations](limitations.md).

**Dispatch on the `type` string.** Renderers call `render_<type>`, transformers call `visit_<type>` and the validator calls `_validate_<type>`. New node types therefore need no changes to the core: create a node with a new `type` and add a method with the matching name. Extensions rely on this when they attach `render_keyboard_key` or `render_strikethrough` to a renderer instance.

**Registries filled on import.** `ParserRegistry` and `RendererRegistry` are class-level dictionaries. Each adapter or renderer module registers itself at the bottom of the file, so a name is available only after its module has been imported. `TransformerRegistry` exists but nothing registers into it by default.

**Configuration as plain dictionaries.** Every parser, renderer, transformer and extension takes an optional `config` dictionary and reads keys with defaults. Unknown keys are ignored, so a misspelt key fails silently. The tables on each page list the keys the code actually reads.

**Extensions work after parsing.** The shipped extensions find their syntax by inspecting the finished tree (for example, searching text nodes for `++…++`) rather than by adding tokenizer rules. This keeps them independent of the backend, but it means they only see syntax that survived parsing as text.

**Logging off by default.** Every module logs through `loguru` at debug or info level. The package disables its logger on import so library users see nothing unless they call `logger.enable("marktripy")`.

## Background research

The `ref/` directory in the repository holds the research notes that led to this design: `ref1.md`, `ref2.md` and `ref3.md` compare Python Markdown libraries (`markdown`, `markdown2`, `mistune`, `marko`, `markdown-it-py`, `mistletoe` and others) on AST access, extensibility and round-trip support.
