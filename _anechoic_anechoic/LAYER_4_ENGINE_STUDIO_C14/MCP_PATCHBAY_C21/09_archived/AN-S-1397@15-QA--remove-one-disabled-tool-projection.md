---
atom_family: SPEC
atom_id: AN-S-1397
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Remove one disabled Tool projection

# Remove one disabled Tool projection

## Claim checked

Registry reconciliation removes a projection whose source Tool is disabled.

## Test case

Disable one previously exposed current Tool **and** regenerate the registry.

## Acceptance criteria

the resulting complete registry excludes that Tool **and** retains **every** other eligible current source.

## Failure disposition

Stop **when** a stale **or** independently allowlisted projection remains.
