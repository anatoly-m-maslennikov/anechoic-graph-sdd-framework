---
atom_family: SPEC
atom_id: AN-S-3871
container:
  component: C21
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 11
  updated_at: 2026-10-24 06:07:28 +0400
---
## Summary

Project one callable MCP Tool from one Tool unit

# Project one callable MCP Tool from one Tool unit

## Applicable when

Apply **when** a validated active immediate Tool unit is selected for MCP exposure.

## Procedure

1. Derive one stable MCP identity from the canonical Tool identity.
2. Project the validated Tool contract **without** splitting, aliasing, **or** aggregating it.
3. Verify that no other source Tool projects **to** the same callable MCP identity.

## Outcome

One valid active Tool unit has exactly one unambiguous callable MCP projection.

## Failure or stop

Stop publication on a missing source, duplicate identity, alias, **or** attempted aggregation.
