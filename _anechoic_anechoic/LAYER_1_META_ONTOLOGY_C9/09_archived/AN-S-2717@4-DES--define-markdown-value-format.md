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
  version: 4
  updated_at: 2026-11-11 16:04:42 +0400
---
## Summary

Define markdown value Format

## Claim

### Prose Claim


The markdown Format admits Markdown source. A section value preserves its markup. Its retrieved value includes its heading and descendant sections.

### Formal Claim

```CFEL
# model
Format//markdown ((INSTANCE_OF)) Format;
```
