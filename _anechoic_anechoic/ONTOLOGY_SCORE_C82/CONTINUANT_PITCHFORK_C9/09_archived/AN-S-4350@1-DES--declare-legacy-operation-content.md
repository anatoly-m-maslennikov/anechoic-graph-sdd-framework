---
atom_family: SPEC
atom_id: AN-S-4350
container:
  component: C9
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-08 18:59:53 +0400
---

## Summary

Declare legacy Operation content

## Claim

### Prose Claim

An Operations Atom may retain its legacy Operation section during migration. Operation is a Markdown Content Property. Its presentation subheadings, lists and code blocks remain part of its value.

### Formal Claim

```CFEL
# model
Atom/(.Header.Role := Operations).Content.Operation:: [markdown]{::0..1};

Atom/(.Header.Role := Operations).Content.Operation.*[]{::0}
```

## Semantics

Operation is the operation text carried by the legacy Operations Atom. This declaration describes that existing section; it does not decide whether a later Form must use Operation or Claim.
