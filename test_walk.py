#!/usr/bin/env python3
# Quick test of walk method

from marktripy.core.ast import Document, Heading, Paragraph, Text

doc = Document()
h1 = Heading(level=1)
h1.add_child(Text("Title"))
doc.add_child(h1)

para = Paragraph()
para.add_child(Text("Some "))
para.add_child(Text("text"))
doc.add_child(para)

# Test walk method
all_nodes = doc.walk()
for _i, _node in enumerate(all_nodes):
    pass
