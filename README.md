
# `marktripy`

`marktripy` is a Python package that you can use from Markdown to AST to Markdown. 

## Original research

For each of these Python packages (the `pip` installation name is given below): 

```
Markdown markdown2[all] myst-docutils marko tree-sitter-markdown umarkdown[cli] markdown-it-py[linkify,plugins] markdown-it-pyrs 
```

1. Research how I can use the package to programmatically convert Markdown to HTML.

2. Research how I can use the package to convert Markdown to some intermediate format, then downgrade head Markdown heading by one level, and also add an ID to the heading, and then serialize the result back to Markdown.

3. Research how I can extend the package with additional constructs (for parsing, for serializing back into the same construct, and for converting into HTML). For example, I’d like to convert Markdown f"++{content}++" into HTML f"<kbd>{content}</kbd>".

4. Research additional Python packages that can be used to convert Markdown to an object structure and back. 

Note: When I say "Markdown", I mean a syntax that can be Markdown, CommonMark, GFM or other Markdown-like syntaxes.

### Results

- @ref/ref1.md
- @ref/ref2.md
- @ref/ref3.md

