---
atom_family: SPEC
atom_id: AN-S-4
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-23 03:18:40 +0400
---
## Summary

Classify structural relocation as MOVE

# Classify structural relocation as MOVE

## Claim checked

relocation of an unchanged governed file identity is classified as `MOVE` **when** **only** its Carrier directory changes; this classification does **not** by itself prove Project conformance.

## Test case

supply a trigger for an admitted Carrier-only relocation within the same owning Scope Unit. preserve the filename, content, Atom identity, Claim, Atom Scope, Claim Scope, authored semantic Relations **and** Version under CA-R-1433 **and** CA-D-304. choose a destination admitted by the applicable Carrier rules; do **not** silently transfer ownership **to** another Scope Unit.

## Acceptance criteria

- provisional context reports `MOVE`, preserves Version, records both repository-relative paths **and** resolves the same authored Relations.
- no context-gathering mutation occurs. an observed nonconforming move is preserved as an observation rather than silently repaired **or** certified conforming.
- a transfer that changes ownership, a governed filename token **or** another semantic value is outside this unchanged-Carrier fixture; do **not** force it into the Version-preserving success case.

## Failure disposition

reject incorrect change classification, lost **before**/**after** paths, an invented Version change for the conforming fixture **or** a claimed preservation of semantic values that actually changed.
