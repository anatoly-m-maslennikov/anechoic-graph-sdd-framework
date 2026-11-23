---
atom_family: SPEC
atom_id: AN-S-1287
container:
  component: C15
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 11
  updated_at: 2026-10-22 12:45:09 +0400
---
## Summary

Reject I/O during object construction

# Reject I/O during object construction

## Claim checked

one PROGRAMMATIC object is constructed **without** acquiring resources **or** applying
external effects.

## Test case

construct one object while its declared resource boundary is unavailable **and**
observe whether construction attempts filesystem, process, network,
persistence, **or** logging-export I/O.

## Acceptance criteria

pass **only** **when** construction completes **without** I/O **and** acquisition begins **only**
through a specifically named explicit method.

## Failure disposition

reject the object lifecycle **until** acquisition is removed from construction.

## Sources

- [CA-M-408 — Allocate owned state and lifecycle to objects](../05_method/CA-M-408-PROGRAMMATIC-STANDARD-IMPLEMENTATION_METHOD--allocate-owned-state-and-lifecycle-to-objects.md)
