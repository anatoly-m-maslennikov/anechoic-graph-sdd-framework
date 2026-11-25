---
atom_family: SPEC
atom_id: AN-S-2006
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 6
  updated_at: "2026-11-25T19:35:31.401729+00:00"
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

