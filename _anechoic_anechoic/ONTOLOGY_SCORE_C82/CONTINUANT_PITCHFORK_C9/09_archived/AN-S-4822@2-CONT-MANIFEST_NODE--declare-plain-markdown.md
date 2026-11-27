---
atom_family: SPEC
atom_id: AN-S-4822
concern:
  subject: Plain Markdown
  path: Model/Carrier/File//Non-executable File//Markdown
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T17:13:49.181834+00:00"
---

## Summary

Declare Plain Markdown

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Markdown

class PlainMarkdown(Markdown):
    pass
```
