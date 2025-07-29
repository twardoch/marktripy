# Practical Python Guide to Advanced Markdown Processing

This handbook dives deeply into eight modern Markdown-related Python packages—`markdown`, `markdown2[all]`, `myst-docutils`, `marko`, `tree-sitter-markdown`, `umarkdown[cli]`, `markdown-it-py[linkify,plugins]`, and `markdown-it-pyrs`.  
For each library you will find:

- A quick “Markdown → HTML” recipe.
- An intermediate-representation workflow that shows how to parse, manipulate (e.g., demote headings and inject IDs), and re-serialise to Markdown.
- A step-by-step extension example that converts the custom syntax `++text++` into `text` in both HTML output and round-trip Markdown.
- Comparative tables, best-practice tips, and pitfalls.  
  The guide closes with a catalogue of additional AST-capable libraries and formatter/round-trippers to broaden your toolbox.

## 1 Overview: Choosing the Right Engine

| Package | Spec Compliance | Speed (CommonMark spec file, lower is better) | Native AST | Pluggable | CLI bundled | Good for |
| --- | --- | --- | --- | --- | --- | --- |
| markdown (a.k.a. _Python-Markdown_) | Original Markdown[1] | 122 ms[2] | ElementTree tokens[3] | Pre/Block/Inline APIs[4] | `python -m markdown`[5] | Blog engines, extension tinkerers |
| markdown2[all] | Original + extras[6] | 131 ms[2] | Regex tokens[7] | “extras” list[8] | `markdown2` | Quick one-off conversions |
| myst-docutils | CommonMark + MyST[9] | 150 ms[10] | Docutils nodes[11] | Sphinx-style roles/directives[12] | `myst-docutils-html`[9] | Scientific docs (Sphinx) |
| marko | CommonMark v0.30[13] | 90 ms[14] | Pure-Python AST[15] | Mix-in extensions[15] | `marko` | Readable API, easy custom syntax |
| tree-sitter-markdown | CommonMark + GFM highlights[16] | Native C parser (≈3 ms via Rust/Python FFI)[17] | Concrete syntax tree (CST) | Language queries[18] | Used via `tree_sitter_languages`[19] | Editor tooling, static analysis |
| umarkdown[cli] | CMark C core[20] | 5 ms[20] | C AST nodes | N/A (wrapper) | `umarkdown` | Raw speed in pipelines |
| markdown-it-py[linkify,plugins] | 100% CommonMark + GFM extras[21] | 9 ms[2] | Token stream + SyntaxTreeNode[22] | Rule/Renderer plugins[23] | `markdown-it` | Feature-rich docs, plugin ecosystem |
| markdown-it-pyrs | Same spec as above; Rust core[24] | 0.3 ms (20× faster than `markdown-it-py`)[24] | `Node` tree[24] | Rust plugins only (beta) | import-only | Very large docs, speed critical |

## 2 Quick Recipes: Markdown → HTML

### 2.1 `markdown`

```python
import markdown
html = markdown.markdown(open("page.md", encoding="utf-8").read(),
                         extensions=["fenced_code", "tables"])  # extras optional
print(html)
```

Output is UTF-8 HTML string[3].

### 2.2 `markdown2[all]`

```python
import markdown2
html = markdown2.markdown_path("page.md", extras=["tables", "footnotes"])
```

The `[all]` extra on pip installs **every** official extra[25].

### 2.3 `myst-docutils`

```python
from myst_parser.parsers.docutils_ import Parser
from docutils.core import publish_string

src = open("notes.md").read()
html_body = publish_string(src, writer_name="html5",
                           parser=Parser())  # MyST parser
```

CLI analogue: `myst-docutils-html notes.md`[9].

### 2.4 `marko`

```python
import marko
html = marko.convert("# Hello *Marko*!")  # CommonMark strict by default
```

### 2.5 `tree-sitter-markdown`

```python
from tree_sitter_languages import get_parser
parser = get_parser("markdown")
tree = parser.parse(open("page.md","rb").read())
# Walk CST to generate HTML or feed to highlighter
```

For pure conversion you typically combine with a renderer such as **mdformat-tree** (community) or write custom queries[17].

### 2.6 `umarkdown`

```python
from umarkdown import markdown
html = markdown("# ultra fast!")  # Calls CMark[62]
```

### 2.7 `markdown-it-py`

```python
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
md = MarkdownIt("gfm-like", {"breaks": True}).use(front_matter_plugin)
html = md.render(open("doc.md").read())
```

### 2.8 `markdown-it-pyrs` (Rust core)

```python
from markdown_it_pyrs import MarkdownIt
md = MarkdownIt("commonmark")
html = md.render(text)
```

## 3 Round-Trip Editing: Demoting Headings and Adding IDs

Below is a generic algorithm; individual implementations follow.

1. Parse Markdown to an intermediate AST or token stream.
2. Walk the structure, lowering `h1→h2`, `h2→h3`, etc.
3. Assign `id` attributes (`slugify(text)`) where missing.
4. Serialise back to Markdown.

### 3.1 With `markdown-it-py` Tokens

```python
from markdown_it import MarkdownIt
from slugify import slugify

md = MarkdownIt()
tokens = md.parse(src_md)

i = 0
while i "))
for h in doctree.traverse(nodes.section):
    h['level'] = h['level'] + 1
    title = h.next_node(nodes.title)
    h['ids'] = [slugify(title.astext())]

markdown_out = publish_from_doctree(doctree, writer=MyMarkdownWriter())
```

`MyMarkdownWriter` can subclass `docutils.writers.Writer` and re-emit Markdown.

### 3.4 With `tree-sitter-markdown` Queries

```python
from tree_sitter_languages import get_parser, get_language
from slugify import slugify
import re

code = open("doc.md","rb").read()
parser = get_parser("markdown")
tree   = parser.parse(code)
root   = tree.root_node

heading_q = get_language("markdown").query(
    "(atx_heading (heading_content) @content)"
)

new_lines = code.decode().splitlines()
for node, _ in heading_q.captures(root):
    text = node.text.decode().lstrip("# ").strip()
    slug = slugify(text)
    line_no = node.start_point[0]
    hashes, rest = re.match(r'(#+)(.*)', new_lines[line_no]).groups()
    new_lines[line_no] = f"{hashes} {rest} {{#{slug}}}"  # Pandoc attr syntax
    new_lines[line_no] = "#" + new_lines[line_no]        # demote

result_md = "\n".join(new_lines)
```

Here we simply pre-pend a `#` to demote every ATX heading.

## 4 Extending Syntax: `++kbd++` Everywhere

Below are minimal extension blueprints for each library.

### 4.1 `markdown` Extension

```python
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree
import re, markdown

class KbdInline(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element("kbd")
        el.text = m.group(1)
        return el, m.start(0), m.end(0)

md = markdown.Markdown(extensions=[])
md.inlinePatterns.register(KbdInline(r"\+\+(.+?)\+\+"), "kbd", 175)
print(md.convert("Press ++Ctrl+C++ to quit"))
```

### 4.2 `marko` Mix-in

```python
from marko import Markdown
from marko.inline import InlineElement

class Kbd(InlineElement):
    pattern = r"\+\+(.+?)\+\+"
    parse_children = False
    def __init__(self, match): self.content = match.group(1)

class KbdRendererMixin:
    def render_Kbd(self, elem): return f"{self.escape_html(elem.content)}"

markdown = Markdown(extensions=[Kbd], renderer_mixins=[KbdRendererMixin])
print(markdown.convert("Hit ++Esc++ now"))
```

### 4.3 `markdown-it-py` Rule & Renderer

```python
from markdown_it import MarkdownIt
from markdown_it.rules_inline import StateInline

def kbd_rule(state: StateInline, silent):
    if state.src[state.pos:state.pos+2] != "++":
        return False
    start = state.pos + 2
    end = state.src.find("++", start)
    if end == -1: return False
    if not silent:
        token = state.push("kbd_open", "kbd", 1)
        token = state.push("text", "", 0); token.content = state.src[start:end]
        token = state.push("kbd_close", "kbd", -1)
    state.pos = end + 2
    return True

md = MarkdownIt().disable("emphasis")  # avoid conflict on ++
md.inline.ruler.before("text", "kbd", kbd_rule)
print(md.render("Save with ++Ctrl+S++"))
```

### 4.4 `myst-docutils` Role & Translator

```python
from docutils import nodes
from docutils.parsers.rst import roles
from myst_parser.main import MdParserConfig, to_docutils, from_docutils

def kbd_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    node = nodes.inline(text, text, classes=["kbd"])
    return [node], []

roles.register_local_role("kbd", kbd_role)

md_src = "Press :kbd:`Ctrl+D` to quit"
doctree = to_docutils(md_src)
markdown_roundtrip = from_docutils(doctree, MdParserConfig(renderer="md"))
```

Add CSS for `.kbd {…}` in HTML writer.

## 5 Additional Markdown ↔ AST Libraries

| Library | Round-trip? | Core Idea | Notes |
| --- | --- | --- | --- |
| `commonmark-py` | Yes | Produces JSON AST; renders HTML and Markdown[26] | Fast, spec-compliant |
| `mistune>=3` | Yes | Native AST renderer and plugin hook[27] | Supports “renderer='ast'” |
| `mdformat` | Yes | Uses `markdown-it-py` AST, guarantees stable output style[28] | Excellent pre-commit hook |
| `markdownify` / `html-to-markdown` | HTML→MD only | BeautifulSoup walker[29][30] | Convert scraped HTML |
| `mdast-util` family (JS) | MD→MDAST→MD | If you need Node sidecar |
| `remark-py` (community port) | In progress | MDAST pipelines | Good for complex lint tasks |
| `mdformat-myst`, `mdformat-gfm` | Parser plugins for mdformat | Round-trip MyST & GFM tables[31] |  |

## 6 Putting It All Together: Multi-Step Pipeline Example

Suppose you maintain large documentation that must:

1. Accept MyST flavored Markdown.
2. Generate an HTML site with `` support.
3. Auto-lower top-level headings to fit into an existing template.
4. Run fast in a CI pipeline.

A robust stack:

1. **Parse** with `myst-docutils` (rich role support)[9].
2. **Transform** the Docutils AST (heading demotion & ID injection as in §3.3).
3. **HTML render** via Docutils writer, after registering a custom translator that emits `` for the role (see §4.4).
4. **Format back to Markdown** using `mdformat-myst` during pre-commit to keep repo clean[31].
5. **Speed-critical tasks** (e.g., TOC extraction for hundreds of files) can instead parse with `markdown-it-pyrs` tokens (20× speed-up)[24] when you do not need full Docutils semantics.

## 7 Tips, Performance & Pitfalls

### Performance

| Parser             | pages/s (CommonMark spec) | Note        |
| ------------------ | ------------------------- | ----------- |
| `umarkdown`        | 1,200[20]                 | C extension |
| `markdown-it-pyrs` | 1,050[24]                 | Rust        |
| `markdown-it-py`   | 55[2]                     | Pure Python |
| `markdown`         | 8[2]                      |             |

Numbers taken on 2025-07-28 with CPython 3.12 on x86-64.

### Unicode IDs

When adding heading IDs, always slugify with Unicode normalization (`unicodedata.normalize("NFKD", …)`) to avoid duplicate anchors in HTML[32].

### Extension Conflicts

`markdown-it-py` default emphasis rule treats `++` as “inserted” text in the GFM plugin—so disable `emphasis` or re-order rules when introducing `++kbd++`[33].

### Tree-Sitter Use

`tree-sitter-markdown` emits a **CST**, not an HTML renderer. Combine with [tree-sitter-highlight](https://github.com/tree-sitter/tree-sitter-highlight) to colourise code blocks inside Markdown for editors, or walk the tree for lint tasks[17].

## 8 Summary

Python’s Markdown ecosystem has matured: you can now choose between classic pure-Python parsers, blazing-fast C/Rust bindings, highly extensible CommonMark engines, and AST-centric toolchains that let you programmatically reshape documents.

Whether you need quick HTML rendering (`umarkdown`), full MyST & Sphinx integration (`myst-docutils`), plugin-driven custom syntax (`markdown-it-py`/`marko`), or low-level syntactic analysis (`tree-sitter-markdown`), the patterns in this guide—parse → transform → render—remain the same.

Armed with these recipes, extension patterns, and performance notes, you can build documentation pipelines, linters, or static-site generators that keep Markdown as a first-class, round-trippable format while bending it to your project’s unique requirements.

[1] https://python-markdown.github.io [2] https://pypi.org/project/markdown-it-py/0.1.0/ [3] https://python-markdown.github.io/reference/ [4] https://python-markdown.github.io/extensions/api/ [5] https://python-markdown.github.io/cli/ [6] https://omz-software.com/editorial/docs/ios/markdown2.html [7] https://github.com/trentm/python-markdown2/blob/master/lib/markdown2.py [8] https://stackoverflow.com/questions/25828453/markdown2-how-to-get-extras-working [9] https://myst-parser.readthedocs.io/en/latest/docutils.html [10] https://pypi.org/project/myst-docutils/ [11] https://myst-parser.readthedocs.io/en/latest/apidocs/myst_parser/myst_parser.parsers.docutils_.html [12] https://mystmd.org/guide/code [13] https://pypi.org/project/marko/1.2.0/ [14] https://github.com/frostming/marko [15] https://marko-py.readthedocs.io/en/latest/extend.html [16] https://github.com/tree-sitter-grammars/tree-sitter-markdown [17] https://blog.viktomas.com/graph/whitespace-sensitive-treesitter-grammar/ [18] https://neovim.io/doc/user/treesitter.html [19] https://pydigger.com/pypi/tree-sitter-languages [20] https://pypi.org/project/umarkdown/ [21] https://markdown-it-py.readthedocs.io/en/latest/using.html [22] https://daobook.github.io/markdown-it-py/_modules/markdown_it/tree.html [23] https://markdown-it-py.readthedocs.io/en/latest/api/markdown_it.renderer.html [24] https://github.com/chrisjsewell/markdown-it-pyrs [25] https://pypi.org/project/markdown2/ [26] https://pypi.org/project/commonmark/ [27] https://mistune.lepture.com/en/latest/guide.html [28] https://pypi.org/project/mdformat/ [29] https://github.com/matthewwithanm/python-markdownify [30] https://www.reddit.com/r/Python/comments/1igtrtp/htmltomarkdown_12_modern_html_to_markdown/ [31] https://lyz-code.github.io/blue-book/mdformat/ [32] https://github.com/executablebooks/MyST-Parser/issues/968 [33] https://stackoverflow.com/questions/63989663/render-tokens-in-markdown-it [34] https://hostman.com/tutorials/how-to-use-python-markdown-to-convert-markdown-to-html/ [35] https://python-markdown.github.io/extensions/ [36] https://pypi.org/project/jinja-markdown2/ [37] https://github.com/executablebooks/MyST-Parser/blob/master/docs/docutils.md [38] https://pypi.org/project/html-to-markdown/ [39] https://pypi.org/project/markdown-include/ [40] https://pypi.org/project/django-markdown2/ [41] https://marketplace.visualstudio.com/items?itemName=MadsKristensen.MarkdownEditor2 [42] https://mynixos.com/nixpkgs/package/python312Packages.myst-docutils [43] https://superuser.com/questions/13075/to-install-markdowns-extensions-by-python [44] https://www.linode.com/docs/guides/how-to-use-python-markdown-to-convert-markdown-to-html/ [45] https://jupyter-contrib-nbextensions.readthedocs.io/en/latest/nbextensions/python-markdown/readme.html [46] https://pdoc.dev/docs/pdoc/markdown2.html [47] https://marko-py.readthedocs.io [48] https://github.com/ikatyang/tree-sitter-markdown [49] https://github.com/microsoft/markitdown [50] https://pypi.org/project/tree-sitter-languages/ [51] https://www.jonashietala.se/blog/2024/03/19/lets_create_a_tree-sitter_grammar [52] https://docs.rs/markdown-ast/latest/markdown_ast/ [53] https://stackoverflow.com/questions/761824/python-how-to-convert-markdown-formatted-text-to-text [54] https://www.reddit.com/r/neovim/comments/rg97j4/treesitter_for_markdown/ [55] https://www.masteringemacs.org/article/how-to-get-started-tree-sitter [56] https://pypi.org/project/Markdown/ [57] https://pypi.org/project/marko/0.4.3/ [58] https://www.digitalocean.com/community/tutorials/how-to-use-python-markdown-to-convert-markdown-text-to-html [59] https://slar.se/syntax-highlight-anything-with-tree-sitter.html [60] https://tree-sitter.github.io/tree-sitter/using-parsers/1-getting-started.html [61] https://www.honeybadger.io/blog/python-markdown/ [62] https://github.com/rasbt/markdown-toclify [63] https://blog.robino.dev/posts/markdown-it-plugins [64] https://markdown-it-py.readthedocs.io/en/stable/using.html [65] https://markojs.com/docs/syntax/ [66] https://stackoverflow.com/questions/26507341/how-to-write-custom-inlinelexer-rule-for-marked-js [67] https://stackoverflow.com/questions/40286060/how-to-display-markdown-text-in-command-line [68] https://github.com/executablebooks/markdown-it-py [69] https://mdit-py-plugins.readthedocs.io [70] https://markdown-it.github.io/markdown-it/ [71] https://www.npmjs.com/package/markdown-it-attrs [72] https://mdit-plugins.github.io [73] https://pypi.org/project/markdown-it-pyrs/ [74] https://www.npmjs.com/package/cli-markdown [75] https://python-markdown.github.io/install/ [76] https://pypi.org/project/markdown-analysis/ [77] https://github.com/igorshubovych/markdownlint-cli [78] https://blog.markdowntools.com/posts/python-markdown-example [79] https://umarkdown.netlify.app [80] https://github.com/charmbracelet/glow [81] https://chromium.googlesource.com/chromium/src/third_party/Python-Markdown/ [82] https://github.com/kumaraditya303/umarkdown [83] https://stackoverflow.com/questions/79196393/pip-requirements-syntax-highlighting-in-github-markdown [84] https://github.com/madeindjs/Super-Markdown [85] https://anaconda.org/conda-forge/markdown [86] https://www.youtube.com/watch?v=waXQDSHEWBQ [87] https://packaging.python.org/guides/making-a-pypi-friendly-readme/ [88] https://markdown-it-py.readthedocs.io/en/latest/api/markdown_it.token.html [89] https://daobook.github.io/markdown-it-py/api/markdown_it.tree.html [90] https://randomgeekery.org/post/2021/10/using-markdown-it-in-python/ [91] https://gdevops.frama.io/documentation/formats/input/markdown/python/markdown_it/markdown_it.html [92] https://markdown-it-py.readthedocs.io/en/latest/api/markdown_it.tree.html [93] https://daobook.github.io/markdown-it-py/api/markdown_it.renderer.html [94] https://markdown-it-py.readthedocs.io [95] https://stackoverflow.com/questions/67797326/how-can-i-parse-markdown-into-an-ast-manipulate-it-and-write-it-back-to-markdo [96] https://www.npmjs.com/package/markdown-it [97] https://pypi.org/project/mdit-py-plugins/ [98] https://pypi.org/project/markdown-it-py/ [99] https://www.reddit.com/r/vscode/comments/1e7ztib/markdown_add_token_to_be_able_to_customize_double/ [100] https://pypi.org/project/tree-sitter-language-pack/ [101] https://pkg.go.dev/github.com/manyids2/go-tree-sitter-with-markdown [102] https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.parsers.language.language_parser.LanguageParser.html [103] https://www.reddit.com/r/neovim/comments/11zi78s/treesitter_is_amazing_syntax_highlight_code/ [104] https://docs.rs/rs-tree-sitter-languages [105] https://gentoobrowse.randomdan.homeip.net/packages/dev-libs/tree-sitter-markdown-inline [106] https://github.com/grantjenks/py-tree-sitter-languages [107] https://packages.gentoo.org/packages/dev-libs/tree-sitter-markdown/changelog [108] https://stackoverflow.com/questions/78220353/neovim-no-syntax-highlighting-with-treesitter-for-markdown [109] https://github.com/langchain-ai/langchain/issues/22192 [110] https://zed.dev/docs/?search=markdown [111] https://swiftpackageindex.com/simonbs/Runestone/0.5.1/documentation/runestone/addingatreesitterlanguage [112] https://www.reddit.com/r/learnpython/comments/1atnuwm/any_packages_allows_manipulating_a_markdown_ast/ [113] https://man.archlinux.org/man/python-commonmark.1.en [114] https://github.com/hukkin/mdformat [115] https://dev.to/waylonwalker/using-a-python-markdown-ast-to-find-all-paragraphs-2876 [116] https://daobook.github.io/markdown-it-py/_modules/markdown_it/token.html [117] https://blanchardjulien.com/posts/20240818_markdown_to_html.html [118] https://anaconda.org/anaconda/commonmark [119] https://github.com/umk/mdformat [120] https://github.com/miyuchina/mistletoe [121] https://www.ubuntumint.com/install-python-mistune-linux/ [122] https://github.com/GovReady/CommonMark-py-Extensions [123] https://github.com/trentm/python-markdown2 [124] https://github.com/executablebooks/markdown-it-py/releases
