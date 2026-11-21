---
atom_family: SPEC
atom_id: AN-S-2804
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 8
  updated_at: 2026-11-11 14:06:22 +0400
---
## Summary

Use distinct graph notation for Node relations

## Claim

### Prose Claim

Treat a Topic as a reference to its declared target. Use the notation in CA-R-1321 and the namespace boundary in CA-R-2483.

- MODEL identifies declared kinds and Properties. Inheritance reuses the original Property Declaration.
- STRUCTURE identifies objects by containment. Containment preserves each object's identity.
- A reverse writing expresses the same Relation fact with swapped endpoints. Each outgoing direction has its own applicable permission and bounds.
