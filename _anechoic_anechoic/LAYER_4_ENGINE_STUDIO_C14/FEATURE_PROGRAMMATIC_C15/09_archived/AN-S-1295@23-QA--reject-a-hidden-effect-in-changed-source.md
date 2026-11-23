---
atom_family: SPEC
atom_id: AN-S-1295
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 23
  updated_at: 2026-11-09 14:19:14 +0400
---

## Summary

Reject a hidden effect in changed source

## Claim

### Prose Claim

one changed effect function declares its complete effect boundary **or** allocates
persistent ownership **to** an object.

## Details

### Test case


Evaluate a changed function that reads the process environment implicitly before writing its declared target, or performs a persistence, Run or Journal write while presented as pure computation.

### Acceptance criteria


Pass only when hidden environment observation is rejected until it is an explicit input or an owned adapter boundary. Persistence and execution recording must be delegated to the declared authorized effect owner or executor; generated output is not durable terminal completion.

### Failure disposition

block the changed unit **until** the hidden observation is removed.

### Sources

- [CA-M-425 — Separate deterministic transformations from effects and lifecycle](../05_method/CA-M-425-PROGRAMMATIC-DIRECT_POLICY--separate-deterministic-transformations-from-effects-and-lifecycle.md)
