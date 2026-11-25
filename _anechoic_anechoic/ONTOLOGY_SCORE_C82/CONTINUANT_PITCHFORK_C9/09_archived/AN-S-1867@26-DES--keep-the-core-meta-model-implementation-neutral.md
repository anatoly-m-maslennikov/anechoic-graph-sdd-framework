---
atom_family: SPEC
atom_id: AN-S-1867
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 26
  updated_at: 2026-10-24 01:37:42 +0400
---
## Summary

Keep the Core Meta-Model implementation neutral

# Summary

Keep the Core Meta-Model implementation neutral

## Scope

CORE_META_MODEL authority and its reusable model invariants and expansion boundaries.

## Claim

CORE_META_MODEL authority **must** define reusable model invariants **and** expansion boundaries **without** hidden dependence on a programming language, LLM provider **or** model, agent host, operating system, repository host, package manager, database, deployment platform, **or** other replaceable implementation mechanism.

mechanism-specific obligations belong **to** the Scope that owns the mechanism. Extensions **and** PROJECT_CONFIGURATION **may** expand the model for their bounded use **without** rewriting its governing Claims.

CORE_META_MODEL **may** name a mechanism **only** **when** the mechanism itself is the explicit Entity governed by the Claim, such as a Carrier format, portability boundary, **or** external constraint; this reference **must not** make that mechanism a hidden prerequisite of unrelated model Claims.

## Details
