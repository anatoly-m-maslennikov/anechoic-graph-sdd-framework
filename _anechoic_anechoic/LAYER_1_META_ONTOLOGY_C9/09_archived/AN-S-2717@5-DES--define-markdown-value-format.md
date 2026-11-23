---
atom_family: SPEC
atom_id: AN-S-2717
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: '2026-11-13T05:17:03.034051+00:00'
---
## Summary

Define markdown value Format

## Claim

### Prose Claim


The markdown Format admits Markdown source. A section value preserves its markup. Its retrieved value includes its heading and descendant sections.

### Formal Claim

```python
# model
relation(source='Format//markdown', name='INSTANCE_OF', target='Format')
```
