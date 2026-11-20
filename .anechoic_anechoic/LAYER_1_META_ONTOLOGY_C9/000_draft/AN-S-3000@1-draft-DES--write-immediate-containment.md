---
identity:
  atom_id: AN-S-3000
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-05 14:25:52 +0400
---
## Summary

Write immediate containment

## Claim

### Prose Claim

`Whole/Part` expresses the immediate CONTAINS Relation from Whole to Part. Its corresponding direct IS_CONTAINED_BY fact runs from Part to Whole. Containment does not imply narrowing or inheritance. When directional cardinality slots are present, the slot before `/` counts outgoing CONTAINS links per Whole, and the slot after `/` counts reverse IS_CONTAINED_BY links per Part. Omitted slots remain unspecified. A Relation declaration or applicable endpoint permission supplies its own bounds.
