---
atom_family: SPEC
atom_id: AN-S-3883
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 17
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Discover only current immediate Tool units

# Discover only current immediate Tool units

## Claim checked

MCP derives its source set from current immediate Tool units rather than helper folders.

## Test case

Add one enabled immediate Tool, one disabled immediate Tool, **and** one nested helper **to** a resolved test topology.

## Acceptance criteria

Discovery includes **only** the enabled immediate Tool **and** reports the other two dispositions explicitly.

## Failure disposition

Stop registry generation on an unresolved source identity.
