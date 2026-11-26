---
atom_family: SPEC
atom_id: AN-S-2717
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 6
  updated_at: "2026-11-25T22:46:56.991355+00:00"
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
