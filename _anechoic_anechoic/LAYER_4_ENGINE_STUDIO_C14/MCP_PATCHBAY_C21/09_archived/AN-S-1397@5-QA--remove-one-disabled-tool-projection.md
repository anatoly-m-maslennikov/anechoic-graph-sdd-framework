---
atom_family: SPEC
atom_id: AN-S-1397
container:
  component: C21
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 5
  updated_at: 2026-09-17 02:10:33 +0000
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
