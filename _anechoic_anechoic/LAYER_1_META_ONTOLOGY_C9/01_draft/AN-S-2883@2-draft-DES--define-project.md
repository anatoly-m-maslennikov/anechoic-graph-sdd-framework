---
atom_family: SPEC
atom_id: AN-S-2883
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: draft
  version: 2
  updated_at: 2026-10-29 00:04:17 +0400
---
# Summary

Define Project

## Claim

Project is the single root Scope Unit. It has no parent Scope Unit and contains the Project's top-level Scope Units. Scope Unit properties apply through specialization, with that explicit root-parent exception. Existing Project Goal Operator ownership remains unchanged.

### Formal claim

```text
Scope Unit/Project
Project > @(Scope Unit)
Project.Parent{0}
```

## Semantics

The slash defines what Project is; the containment relation defines its parts. A child Scope Unit is not a subtype of Project merely because Project contains it.

## Details

CA-A-1258 records this correction. Current predecessor remains unchanged.
