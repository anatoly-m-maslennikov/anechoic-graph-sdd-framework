---
atom_family: SPEC
atom_id: AN-S-4822
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-26T15:54:02.806048+00:00"
---

## Summary

Declare Plain Markdown

## Claim scope

MODEL//ANECHOIC <+ Carrier/File//Non-executable File//Markdown//Plain Markdown

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Markdown

class PlainMarkdown(Markdown):
    pass
```
