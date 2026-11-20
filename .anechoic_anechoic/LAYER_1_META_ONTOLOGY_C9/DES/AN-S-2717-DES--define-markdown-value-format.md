---
identity:
  atom_id: AN-S-2717
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 6
  updated_at: '2026-11-13T22:57:39.635646+00:00'
---
## Summary

Define markdown value Format

## Claim

### Prose Claim


The markdown Format admits Markdown source. A section value preserves its markup. Its retrieved value includes its heading and descendant sections.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(entity_name='markdown')
```
