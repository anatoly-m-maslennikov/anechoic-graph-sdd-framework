---
atom_family: SPEC
atom_id: AN-S-2007
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: active
  version: 6
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Define Markdown Atom Carrier

## Claim

### Prose Claim

A Markdown Atom Carrier is a Markdown File Carrier that represents an Atom.
### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Markdown

class MarkdownAtomCarrier(Markdown):
    pass

declare_entity(entity_class=MarkdownAtomCarrier, entity_name='Markdown Atom Carrier')
```

