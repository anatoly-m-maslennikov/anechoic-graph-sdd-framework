---
atom_family: SPEC
atom_id: AN-S-4037
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 07:32:39 +0400
---
## Summary

Define Structural Unit

## Claim

Structural Unit classifies the organizational Scope Unit kind. Project specializes Scope Unit as its parentless root; structural containment remains separate from this classification and adds no numeric structural level.

### Formal claim

```text
Continuant/Structural Unit
Structural Unit/Scope Unit
Scope Unit/Project
```

## Semantics

Scope Unit specializes Structural Unit; Project specializes Scope Unit as its parentless root. Project containment and recursive Scope Unit structure are separate from this classification. This classification does not add a numeric structural-level property. CA-A-1258 supersedes the earlier sibling Project/Scope Unit layout.

## Details

Review Draft from A1247–A1249; numeric identity is not yet allocated. No Current source, Carrier, implementation file or runtime is changed.
