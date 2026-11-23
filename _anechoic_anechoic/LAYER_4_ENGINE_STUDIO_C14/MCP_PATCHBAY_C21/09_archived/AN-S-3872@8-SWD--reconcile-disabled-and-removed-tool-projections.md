---
atom_family: SPEC
atom_id: AN-S-3872
container:
  component: C21
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 8
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Reconcile disabled and removed Tool projections

# Reconcile disabled and removed Tool projections

## Applicable when

Apply **when** the current Tool source set **or** its enablement decisions change.

## Procedure

1. Resolve the complete current source set **before** changing the registry.
2. Add newly eligible Tools, exclude explicitly disabled Tools, **and** remove projections **without** current sources.
3. Publish **only** the resulting complete set rather than retaining a separate allowlist.

## Outcome

the registry has no stale, disabled, **or** independently configured Tool projection.

## Failure or stop

Stop **when** source discovery is incomplete **or** **any** resulting projection cannot be classified.
