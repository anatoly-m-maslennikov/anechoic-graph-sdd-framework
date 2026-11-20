---
identity:
  atom_id: AN-S-2006
context:
  container:
    component: C9
  tier: 1
  lens: DES
state:
  status: active
  version: 6
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Define Markdown File Carrier

## Claim

### Prose Claim

A Markdown File Carrier is a File Carrier represented using Markdown.
### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import File

class Markdown(File):
    pass

declare_entity(entity_class=Markdown, entity_name='Markdown')
```

