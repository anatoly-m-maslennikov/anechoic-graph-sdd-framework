---
atom_family: SPEC
atom_id: AN-S-1272
container:
  component: C15
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 12
  updated_at: 2026-10-22 12:45:09 +0400
---
## Summary

Recover one partial file write

# Recover one partial file write

## Claim checked

one interrupted PROGRAMMATIC file replacement preserves **or** explicitly reports
its declared recovery boundary **without** guessing at a completed result.

## Applicable conditions

apply **when** a component writes replacement content through a temporary carrier
**or** **otherwise** has a declared partial-write recovery boundary.

## Test case

interrupt one replacement **after** its temporary carrier is prepared but **before**
the declared replacement completes.

## Acceptance criteria

pass **only** **when** the original target **or** a declared recoverable result remains
identifiable, no false completion is reported, **and** the partial state is
diagnosable from the returned context.

## Failure disposition

stop the mutation path **until** its weaker recovery boundary is explicit **or** its
atomic replacement guarantee is restored.

## Sources

- [CA-M-409 — Bound file and subprocess effects](../05_method/CA-M-409-PROGRAMMATIC-STANDARD-IMPLEMENTATION_METHOD--bound-file-and-subprocess-effects.md)
