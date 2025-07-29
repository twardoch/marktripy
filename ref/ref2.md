# Python Libraries for Markdown Parsing and Extension

This report surveys several Python packages for processing Markdown: converting Markdown into HTML; converting Markdown into an intermediate representation (e.g., an abstract syntax tree) so that heading levels can be modified and IDs added; and extending the parser to support new constructs, such as turning `++content++` into `<kbd>content</kbd>`. It also lists additional Python packages that can convert Markdown into an object structure and back.

## 1\. Python‑Markdown (`Markdown`)

| Capability              | How to achieve it                     | Notes |
| ----------------------- | ------------------------------------- | ----- |
| Convert Markdown → HTML | Import the `markdown` module and call |

`markdown.markdown(text, extensions=[…], output_format='html')`. The function takes a string and returns HTML[python-markdown.github.io](https://python- markdown.github.io/reference/#:~:text=markdown.markdown%28text%20%5B%2C%20).| Extensions such as `fenced_code`, `tables`, `toc` etc. may be enabled. Output formats include HTML and XHTML.  
Convert Markdown → AST → modify → back to Markdown| Python‑Markdown represents parsed output as an `xml.etree.ElementTree` element tree. The `Markdown` class exposes a `parser` attribute that holds a [`markdown.blockparser.BlockParser`]. After parsing, the root `ElementTree` is available via `markdown.parser.md.parser.parseDocument`, but there is no official API to go from ElementTree back to Markdown. Developers can modify the tree and then render HTML via `markdown.serializer.to_html_string()`. Converting modified ElementTree back to Markdown is non‑trivial; thus this library is unsuitable for round‑tripping Markdown with modifications.|  
Adding custom constructs| Extensions allow adding new preprocessors, block/inline processors and postprocessors[python- markdown.github.io](https://python- markdown.github.io/extensions/api/#:~:text=). For example, to transform `--text--` into `<del>text</del>`, subclass `markdown.inlinepatterns.InlineProcessor` with a regex pattern matching `--(.*?)--` and define `handleMatch` to return an element node; register the processor in an extension class and load it via `markdown.markdown(text, extensions=[YourExtension])`.| The extension API is well‑documented and supports hooking into pre‑processing, block parsing, inline parsing, tree processing and post‑processing.

**Suitability** – Python‑Markdown excels at HTML conversion and custom syntax via extensions. However, it does not provide an easy intermediate representation for editing and serialising back to Markdown.

## 2\. `markdown2[all]`

| Capability | How to achieve it | Notes |
| --- | --- | --- |
| Convert Markdown → HTML | `markdown2.markdown(text, extras=extras_list)` or |

`markdown2.Markdown(extras=…).convert(text)` returns HTML[raw.githubusercontent.com](https://raw.githubusercontent.com/trentm/python- markdown2/master/README.md#:~:text=As%20a%20module%3A%20%60%60%60python%20,p%3E%5Cn).| Extras can enable features like `tables`, `code-friendly`, `footnotes`, `toc`, etc. The optional `header-ids` extra adds `id` attributes to headings automatically[github.com](https://github.com/trentm/python- markdown2/wiki/Extras#:~:text=http%3A%2F%2Fgithub.github.com%2Fgithub,language%20which%20used%20for%20syntax).  
Convert Markdown → intermediate → modify → back to Markdown| `markdown2` does not expose its internal parse tree and cannot reconstruct Markdown from HTML. Only HTML is produced, so it cannot easily adjust heading levels and IDs before output.|  
Adding custom constructs| `markdown2` has a plugin system called _extras_. Developers can write extras to modify how Markdown is parsed. A custom extra can override or extend the parser; however, documentation and support are limited.|

**Suitability** – best for straightforward Markdown → HTML conversion with prebuilt extras but not for AST modifications or custom syntax.

## 3\. MyST‑Docutils (`myst-docutils`)

MyST‑Parser is a Markdown parser built on top of `markdown-it-py` and integrated with Docutils (the reStructuredText toolkit). The package `myst- docutils` provides command‑line tools and functions.

| Capability | How to achieve it | Notes |
| --- | --- | --- |
| Convert Markdown → HTML | Use `from myst_parser.main import to_html` and call |

`to_html(md_text)`[myst-parser.readthedocs.io](https://myst- parser.readthedocs.io/en/v0.17.2/api/parsers.html#:~:text=Parse%20MyST%20Markdown%20to%20HTML). Alternatively, use the CLI: `myst-docutils-html myfile.md` which reads Markdown and outputs HTML[myst-parser.readthedocs.io](https://myst- parser.readthedocs.io/en/latest/docutils.html#:~:text=On%20installing%20MyST,commands%20are%20made%20available).|  
Convert Markdown → AST → modify → back to Markdown| `from myst_parser.main import to_docutils` returns a Docutils AST; `to_tokens` returns the underlying `markdown-it-py` token stream[myst-parser.readthedocs.io](https://myst- parser.readthedocs.io/en/v0.17.2/api/parsers.html#:~:text=Parse%20MyST%20Markdown%20to%20HTML). Docutils nodes support full tree manipulation. After editing (e.g., demoting heading levels and adding `ids`), call `docutils.writers.html5_polyglot.Writer` to get HTML, or use `docutils.core.publish_from_doctree` with a `writer` for HTML. To serialise back to Markdown, call `myst_parser.main.to_markdown` or use `markdown_it` tokens and a renderer. This allows modifications on the AST and round‑tripping.|  
Adding custom constructs| Extend `markdown-it-py` via a plugin. Write a plugin function that accepts a `MarkdownIt` parser and registers parsing rules and renderers for new syntax. For example, to parse `++text++` as `<kbd>text</kbd>`, implement an inline rule triggered by `+` characters and return tokens; then register a renderer that outputs `<kbd>` tags. Load the plugin in MyST by passing it to `create_md_parser(config, RendererHTML).enable("plugin_name")`[myst-parser.readthedocs.io](https://myst- parser.readthedocs.io/en/v0.17.2/api/parsers.html#:~:text=To%20load%20one%20of%20these,py%60%20parser).| MyST inherits the plugin flexibility of `markdown-it-py`, but some features (e.g., footnotes, math) are already built in.

**Suitability** – provides robust AST editing via Docutils and `markdown-it- py`, and can convert back to Markdown, making it ideal for complex processing.

## 4\. Marko (`marko`)

Marko is a pure‑Python implementation of the CommonMark spec designed for extensibility.

| Capability              | How to achieve it                 | Notes |
| ----------------------- | --------------------------------- | ----- |
| Convert Markdown → HTML | Simple conversion: `import marko; |

marko.convert(text)`returns HTML[marko-py.readthedocs.io](https://marko- py.readthedocs.io/en/latest/#:~:text=Marko%20is%20a%20pure%20Python,in%20the%20Extend%20Marko%20section). The CLI`python3 -m marko -e EXTENSION file.md`does the same. You can choose a different parser or renderer class.| Convert Markdown → AST → modify → back to Markdown| Marko provides an _abstract syntax tree_ (Element) accessible via`marko.block_parser.BlockParser.parse()`. Use `marko.ast_renderer.ASTRenderer`to generate Python objects representing Markdown elements. Modify heading nodes (demote level and add`extra_attrs`such as`id`), then re-render back to Markdown using `marko.ext.gfm.MarkdownRenderer`or your own renderer. Re‑rendering to Markdown is possible via`ASTRenderer`combined with`MarkdownRenderer`.| Adding custom constructs| Marko’s extension API allows adding new inline or block elements. Define a class deriving from `marko.inline.InlineElement`with a regex pattern; implement a`match`or`parse`method to produce the element and store captured content. Next, subclass a renderer mixin to define how this element is rendered into HTML (e.g., wrap content in`<kbd>`). Register the extension using `MarkoExtension(elements=[YourElement], renderer_mixins=[YourRendererMixin])` and pass it into the parser/renderer[marko-py.readthedocs.io](https://marko- py.readthedocs.io/en/latest/\_sources/extend.rst.txt#:~:text=Now%20subclass%20,a%20new%20element%20type)[marko- py.readthedocs.io](https://marko- py.readthedocs.io/en/latest/\_sources/extend.rst.txt#:~:text=).| Marko gives fine‑grained control over both parsing and rendering, enabling full round‑trip editing.

**Suitability** – Marko is a well‑designed extensible library for AST manipulations and custom syntax. It can convert Markdown to HTML and re‑serialise back to Markdown.

## 5\. Tree‑sitter‑Markdown (`tree-sitter-markdown`)

Tree‑sitter is a general parser generator; the `tree-sitter-language-pack` provides Python bindings to various languages including Markdown.

| Capability | How to achieve it | Notes |
| --- | --- | --- |
| Convert Markdown → HTML | Not supported. Tree‑sitter only creates syntax trees; |
| you must walk the tree and implement your own renderer. |
| Convert Markdown → AST → modify → back to Markdown | Use |

`tree_sitter_language_pack.get_parser('markdown')` to get a parser; call `parser.parse(bytes(text, 'utf8'))` to obtain a syntax tree. The tree’s nodes can be traversed and modified, but there is no built‑in serializer to Markdown or HTML. You would need to write your own emitter to produce Markdown or HTML from the tree[pypi.org](https://pypi.org/project/tree-sitter-language-pack/).|  
Adding custom constructs| Not supported in the Python bindings. Tree‑sitter grammar is defined in C; customizing requires building a new grammar.|

**Suitability** – provides a rich syntax tree but requires heavy lifting to render; not recommended for typical Markdown processing tasks.

## 6\. umarkdown (`umarkdown[cli]`)

`umarkdown` is a thin Python wrapper around the CMark library.

| Capability | How to achieve it | Notes |
| --- | --- | --- |
| Convert Markdown → HTML | Use `from umarkdown import markdown; html = |

markdown(text, source_pos=False, hard_breaks=False, no_breaks=False, unsafe=False, smart=False)`[pypi.org](https://pypi.org/project/umarkdown/#:~:text=Usage). The options correspond to CMark flags (`source_pos`adds`data-sourcepos`attributes,`hard_breaks`treats line breaks as`<br />`, `smart`enables typographic replacements)[umarkdown.netlify.app](https://umarkdown.netlify.app/options/#:~:text=%2A%20).| Convert Markdown → AST → modify → back to Markdown| Not supported.`umarkdown`returns only HTML. There is no API to access the parse tree or to serialise back to Markdown.| Adding custom constructs| Not supported.`umarkdown` is a wrapper around CMark and cannot be extended in Python.|

**Suitability** – good for quick conversion to HTML but not for advanced processing or custom syntax.

## 7\. markdown‑it‑py (`markdown-it-py[linkify,plugins]`)

`markdown-it-py` is a Python port of the JavaScript `markdown-it` parser; it is modular and extensible.

| Capability | How to achieve it | Notes |
| --- | --- | --- |
| Convert Markdown → HTML | Create a parser: `from markdown_it import MarkdownIt; |

md = MarkdownIt().enable('linkify').enable('table'); html = md.render(text)`[markdown-it-py.readthedocs.io](https://markdown-it- py.readthedocs.io/en/latest/using.html#:~:text=from%20pprint%20import%20pprint%20from,markdown_it%20import%20MarkdownIt).| Convert Markdown → AST → modify → back to Markdown| Calling `md.parse(text)`returns a list of`Token`objects describing the parse, with properties like`type`, `tag`, `nesting`, and `children`[markdown-it- py.readthedocs.io](https://markdown-it- py.readthedocs.io/en/latest/using.html#:~:text=from%20pprint%20import%20pprint%20from,markdown_it%20import%20MarkdownIt). Use `markdown_it.tree.SyntaxTreeNode`to collapse tokens into a tree; you can traverse and modify nodes (e.g., demote heading tokens and add`attrs`). To reconstruct Markdown, implement a custom renderer or use existing ones (e.g., `markdown-it-py`does not include a Markdown renderer by default, but libraries like`markdown-it`in JavaScript have plugin`markdown-it- serializer`; in Python you can use packages such as `mdformat`).| Adding custom constructs| Add custom rules via `md.inline.ruler.before`or`.after`to register a new tokenizer for the`++`pattern; then define a render rule for`token.type`that outputs`<kbd>`tags[markdown-it- py.readthedocs.io](https://markdown-it- py.readthedocs.io/en/latest/using.html#:~:text=You%20can%20inject%20render%20methods,into%20the%20instantiated%20render%20class). The`mdit-py-plugins`package supplies many optional plugins such as`heading anchors`, `attributes`, `containers`, etc., which can be enabled via `md.use(plugin, options)`[mdit-py-plugins.readthedocs.io](https://mdit-py- plugins.readthedocs.io/en/latest/#:~:text=,32).|

**Suitability** – robust for HTML conversion and custom syntax via plugins. It provides an accessible token stream and syntax tree, but re‑serialising to Markdown requires additional tooling.

## 8\. markdown‑it‑pyrs (`markdown-it-pyrs`)

`markdown-it-pyrs` is a Python binding to the Rust implementation of `markdown-it`. It emphasizes speed and a direct node tree.

| Capability | How to achieve it | Notes |
| --- | --- | --- |
| Convert Markdown → HTML | Initialise: `from markdown_it_pyrs import MarkdownIt; |

md = MarkdownIt('commonmark')`and call`html = md.render(text)`to produce HTML[raw.githubusercontent.com](https://raw.githubusercontent.com/chrisjsewell/markdown- it- pyrs/main/README.md#:~:text=%60markdown,offset%2C%20rather%20than%20line%20only). You can enable optional plugins like`linkify`, `strikethrough`, `footnote`etc. via`.enable()`or`.enable_many()`[raw.githubusercontent.com](https://raw.githubusercontent.com/chrisjsewell/markdown- it-pyrs/main/README.md#:~:text=).| Convert Markdown → AST → modify → back to Markdown| `md.tree(text)`returns a`Node`tree where each node corresponds to a Markdown element[raw.githubusercontent.com](https://raw.githubusercontent.com/chrisjsewell/markdown- it- pyrs/main/README.md#:~:text=%60markdown,offset%2C%20rather%20than%20line%20only). Each node has an`attrs`dictionary and`children`list. To modify attributes, you must reassign them (e.g.,`node.attrs = node.attrs| {'id': 'heading'}`) because the dictionary is a copy:contentReference[oaicite:21]{index=21}. After modifications, call `node.render()`to output HTML. However, there is no built‑in serializer back to Markdown. Adding custom constructs| Currently`markdown-it-pyrs`does not support writing parser plugins in Python; plugin support is limited to compiled Rust features[raw.githubusercontent.com](https://raw.githubusercontent.com/chrisjsewell/markdown- it-pyrs/main/README.md#:~:text=). Therefore, custom syntax like`++` cannot be added.|

**Suitability** – extremely fast and great for HTML conversion; provides a tree structure for modifications and HTML rendering but no round‑trip to Markdown or custom syntax in Python.

## 9\. Additional Python Packages for Markdown → Object → Markdown

Several other libraries can parse Markdown into an object representation and often convert back to Markdown or HTML.

### Mistune

Mistune is a fast, pure‑Python Markdown parser that is highly extensible.

- **HTML conversion** – Use `mistune.html(text)` or create a Markdown parser via `mistune.create_markdown(renderer=mistune.HTMLRenderer(), plugins=[…])`[mistune.lepture.com](https://mistune.lepture.com/en/latest/guide.html#:~:text=Mistune%20is%20super%20easy%20to,Markdown%20formatted%20text%20into%20HTML).

- **Accessing and editing AST** – Pass `renderer=None` to `mistune.create_markdown()` to obtain a list of tokens (an AST). Mistune also offers a `MarkdownRenderer` that can serialise tokens back to Markdown[mistune.lepture.com](https://mistune.lepture.com/en/latest/renderers.html#:~:text=,self%2C%20text%2C%20rt). You can adjust heading levels by modifying tokens and re‑rendering using this renderer.

- **Custom constructs** – Subclass `HTMLRenderer` to override how tokens are rendered, or define new tokens via `plugins`. For example, to implement `++text++` as a `<kbd>` tag you would write a plugin that defines a pattern for `++` and returns a token, then provide a renderer method that outputs `<kbd>` around the content. Mistune’s plugin system makes such customisation straightforward[mistune.lepture.com](https://mistune.lepture.com/en/latest/renderers.html#:~:text=Markdown%20Renderer%C2%B6).

### Mistletoe

Mistletoe is another pure‑Python Markdown parser emphasising ASTs.

- **AST** – Use `Document.read()` to parse Markdown into a `Document` (AST). You can traverse this tree and modify nodes; the library provides a `walk()` function to iterate through nodes[mistletoe-ebp.readthedocs.io](https://mistletoe-ebp.readthedocs.io/en/latest/using/intro.html#:~:text=Programmatic%20Use%C2%B6).

- **HTML conversion** – `HTMLRenderer().render(doc)` turns the AST into HTML[mistletoe-ebp.readthedocs.io](https://mistletoe-ebp.readthedocs.io/en/latest/using/intro.html#:~:text=Programmatic%20Use%C2%B6).

- **Custom constructs** – The developer guide demonstrates how to create a custom token by subclassing `SpanToken` with a regex pattern and implementing `parse()`; then subclass `HTMLRenderer` to render the new token. For example, to convert `[[alt|target]]` into a wiki link, you implement a `GitHubWiki` token and define a renderer method[pypi.org](https://pypi.org/project/mistletoe/0.1.1/#:~:text=GitHub%20wiki%20links%20are%20span,SpanToken). Similarly, one could parse `++text++` to produce a `<kbd>` element[pypi.org](https://pypi.org/project/mistletoe/0.1.1/#:~:text=import%20mistletoe). Mistletoe also supports custom Markdown renderers.

### CommonMark (commonmark.py)

This library provides Python bindings for the reference CommonMark parser.

- **HTML conversion** – Use `commonmark.commonmark(text)` to convert to HTML. For manual control, parse with `Parser().parse(text)` to get a `Node` tree and then render with `HtmlRenderer()`[pypi.org](https://pypi.org/project/commonmark/#:~:text=Usage).

- **AST editing** – The AST is accessible via the `Node` objects. You can traverse and modify it; however, there is no built‑in serializer to Markdown, only to HTML.

- **Custom constructs** – The parser is not easily extensible in Python because grammar is fixed.

### cmarkgfm & paka.cmark

`cmarkgfm` and `paka.cmark` are bindings to GitHub’s `cmark` C library with GitHub Flavored Markdown. They provide functions like `markdown_to_html(text)` to convert to HTML[pypi.org](https://pypi.org/project/cmarkgfm/#:~:text=High,To%20render%20normal%20CommonMark). They do not expose ASTs or support custom syntax. The dev article emphasises that these libraries are simple and fast but not extensible[dev.to](https://dev.to/bowmanjd/processing-markdown-in-python- using-available-commonmark-implementations-cmarkgfm-paka-cmark-and- mistletoe-350a#:~:text=cmarkgfm).

### Pandoc & panflute (honourable mention)

While not in the requested list, Pandoc (via `panflute`) deserves mention. `panflute` is a Python library for writing Pandoc filters. It reads a Pandoc AST (JSON) representing Markdown, allows modifications (e.g., demoting heading levels and adding attributes), and writes back to Markdown or HTML using Pandoc. It is extremely powerful for complex transformations but requires Pandoc installed.

## 10\. Summary Comparison

The following table summarises the key capabilities for each library:

Library| HTML conversion| Intermediate structure & heading editing| Custom syntax support| Notes  
---|---|---|---|---  
**Python‑Markdown** (`Markdown`)| Built‑in: `markdown.markdown(text)`[python- markdown.github.io](https://python- markdown.github.io/reference/#:~:text=markdown.markdown%28text%20%5B%2C%20)| ElementTree but no built‑in way to convert back to Markdown; editing is possible only before HTML rendering| Yes – via extension API; implement custom processors[python-markdown.github.io](https://python- markdown.github.io/extensions/api/#:~:text=)| Best for HTML conversion and custom extensions; not ideal for round‑tripping.  
**markdown2**| `markdown2.markdown(text)`[raw.githubusercontent.com](https://raw.githubusercontent.com/trentm/python- markdown2/master/README.md#:~:text=As%20a%20module%3A%20%60%60%60python%20,p%3E%5Cn)| None; no AST or round‑trip| Limited extras; not well‑documented| Simple conversion.  
**MyST‑docutils**| `to_html(text)` or CLI[myst- parser.readthedocs.io](https://myst- parser.readthedocs.io/en/v0.17.2/api/parsers.html#:~:text=Parse%20MyST%20Markdown%20to%20HTML)[myst- parser.readthedocs.io](https://myst- parser.readthedocs.io/en/latest/docutils.html#:~:text=On%20installing%20MyST,commands%20are%20made%20available)| Full Docutils AST and tokens; can demote headings and add IDs; `to_markdown` for round‑trip| Yes – via `markdown-it-py` plugin architecture[myst- parser.readthedocs.io](https://myst- parser.readthedocs.io/en/v0.17.2/api/parsers.html#:~:text=To%20load%20one%20of%20these,py%60%20parser)| Best choice for complex processing.  
**Marko**| `marko.convert(text)`[marko-py.readthedocs.io](https://marko- py.readthedocs.io/en/latest/#:~:text=Marko%20is%20a%20pure%20Python,in%20the%20Extend%20Marko%20section)| AST via `ASTRenderer`; modify and re‑render via `MarkdownRenderer`| Yes – via custom element classes and renderer mixins[marko- py.readthedocs.io](https://marko- py.readthedocs.io/en/latest/\_sources/extend.rst.txt#:~:text=Now%20subclass%20,a%20new%20element%20type)[marko- py.readthedocs.io](https://marko- py.readthedocs.io/en/latest/\_sources/extend.rst.txt#:~:text=)| Flexible and extensible.  
**Tree‑sitter‑Markdown**| None| Provides syntax tree but no serializer[pypi.org](https://pypi.org/project/tree-sitter-language-pack/)| No (grammar in C)| For low‑level parsing only.  
**umarkdown**| `umarkdown.markdown(text)`[pypi.org](https://pypi.org/project/umarkdown/#:~:text=Usage)| None| None| Lightweight CMark wrapper.  
**markdown‑it‑py**| `MarkdownIt().render(text)`[markdown-it- py.readthedocs.io](https://markdown-it- py.readthedocs.io/en/latest/using.html#:~:text=from%20pprint%20import%20pprint%20from,markdown_it%20import%20MarkdownIt)| Token stream and `SyntaxTreeNode`; round‑trip requires separate renderer| Yes – via custom rules and plugin system[markdown-it- py.readthedocs.io](https://markdown-it- py.readthedocs.io/en/latest/using.html#:~:text=You%20can%20inject%20render%20methods,into%20the%20instantiated%20render%20class)[mdit- py-plugins.readthedocs.io](https://mdit-py- plugins.readthedocs.io/en/latest/#:~:text=,32)| Good plugin ecosystem; pair with `mdformat` for Markdown output.  
**markdown‑it‑pyrs**| `MarkdownIt('commonmark').render(text)`[raw.githubusercontent.com](https://raw.githubusercontent.com/chrisjsewell/markdown- it- pyrs/main/README.md#:~:text=%60markdown,offset%2C%20rather%20than%20line%20only)| Node tree; can modify and call `node.render()` (HTML)[raw.githubusercontent.com](https://raw.githubusercontent.com/chrisjsewell/markdown- it- pyrs/main/README.md#:~:text=%60markdown,offset%2C%20rather%20than%20line%20only); no Markdown serializer| No Python‑side plugins[raw.githubusercontent.com](https://raw.githubusercontent.com/chrisjsewell/markdown- it-pyrs/main/README.md#:~:text=)| Extremely fast; limited customisation.

## Recommendations

- **For simple Markdown → HTML conversion** : use `markdown2`, `umarkdown`, `cmarkgfm`, `paka.cmark` or `markdown‑it‑pyrs` (fastest). `Python‑Markdown` also works and is widely supported.

- **For editing headings and adding IDs with round‑trip to Markdown** : use **MyST‑docutils** or **Marko**. They expose ASTs and provide methods to re‑serialise to Markdown. Mistune also offers AST editing and Markdown rendering, albeit outside the core list of packages.

- **For custom syntax (e.g.,`++text++` → `<kbd>`)**: use **Python‑Markdown** (write a custom inline processor), **MyST‑docutils** (write a `markdown-it-py` plugin), **Marko** (write an extension class and renderer mixin), or **Mistune** / **Mistletoe** if exploring beyond the given list. `markdown‑it‑py` can also handle this via its plugin system.

These tools provide various trade‑offs between speed, extensibility and round‑trip editing. For complex workflows such as modifying an AST and returning to Markdown while supporting custom syntax, MyST‑docutils and Marko stand out.
