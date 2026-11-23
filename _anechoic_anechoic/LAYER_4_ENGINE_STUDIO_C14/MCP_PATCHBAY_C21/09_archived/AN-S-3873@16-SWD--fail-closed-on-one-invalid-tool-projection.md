---
atom_family: SPEC
atom_id: AN-S-3873
container:
  component: C21
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 16
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Fail closed on one invalid Tool projection

# Fail closed on one invalid Tool projection

## Applicable when

Apply **when** descriptor validation detects one invalid Tool **or** Workflow binding.

## Procedure

1. Retain the complete candidate frontier and identify the invalid capability and exact invalid descriptor field.
2. Quarantine that capability, remove any stale projection for it, and emit its explicit diagnostic without repairing, invoking, or reinterpreting it.
3. Publish every independently valid current descriptor in the same generation and retain truthful unavailable-capability evidence for the quarantined descriptor.

## Outcome

MCP never exposes an invalid or stale descriptor as current, and one invalid descriptor does not withdraw an unrelated valid capability.

## Failure or stop

Stop exposure of the invalid capability until its source or ambiguity is resolved. Stop the entire registry only when generator integrity or the common activated descriptor frontier is unresolved.
