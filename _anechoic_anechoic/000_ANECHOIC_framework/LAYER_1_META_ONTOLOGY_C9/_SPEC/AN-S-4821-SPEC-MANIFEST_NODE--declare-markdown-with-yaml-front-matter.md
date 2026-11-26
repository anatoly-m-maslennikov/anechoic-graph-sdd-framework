---
atom_family: SPEC
atom_id: AN-S-4821
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 1
  updated_at: '2026-11-24T00:00:00+00:00'
---

## Summary

Declare Markdown with YAML Front Matter

## Claim scope

MODEL//ANECHOIC <+ Carrier/File//Non-executable File//Markdown//Markdown with YAML Front Matter

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Markdown

class MarkdownWithYAMLFrontMatter(Markdown):
    pass
```
