---
atom_family: SPEC
atom_id: AN-S-2804
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 12
  updated_at: "2026-11-25T23:05:47.674937+00:00"
---
## Summary

Use distinct graph notation for Node relations

## Claim

### Prose Claim

Treat a Topic as a reference to its declared target. Use the notation in CA-R-1321 and the Model and Project Structure distinction in AN-S-3093.

- MODEL identifies declared kinds and Properties. Inheritance reuses the original Property Declaration.
- STRUCTURE identifies objects by containment. Containment preserves each object's identity.
- A reverse writing expresses the same Relation fact with swapped endpoints. Each outgoing direction has its own applicable permission and bounds.
