---
atom_family: SPEC
atom_id: AN-S-2883
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-26T19:17:02.461683+00:00"
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
