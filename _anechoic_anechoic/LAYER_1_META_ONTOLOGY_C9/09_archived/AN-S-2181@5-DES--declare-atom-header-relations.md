---
atom_family: SPEC
atom_id: AN-S-2181
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: 2026-11-08 20:06:37 +0400
---
## Summary

Declare Atom.Header.Relations

## Claim

### Prose Claim

Each child name is the canonical name of a declared Relation, and each child has one or more base Atom ID values. A present Relations group has at least one child.

The replacement Atom stores IS_REPLACEMENT_FOR with its predecessor Atom IDs.

### Formal Claim

```CFEL
# model
Atom.Header.Relations{::0..1} :: []{::0};

Atom.Header.Relations.*[string]{::1+};

Atom.Header.Relations.* :: [string]{::1+}
```
