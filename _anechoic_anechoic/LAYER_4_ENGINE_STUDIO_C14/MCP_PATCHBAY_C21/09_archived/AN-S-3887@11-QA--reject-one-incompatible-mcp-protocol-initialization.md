---
atom_family: SPEC
atom_id: AN-S-3887
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 11
  updated_at: 2026-10-24 06:07:28 +0400
---
## Summary

Reject one incompatible MCP protocol initialization

# Reject one incompatible MCP protocol initialization

## Claim checked

MCP initialization admits **only** a declared compatible protocol revision **and** capability set.

## Test case

Initialize with one unsupported required protocol capability.

## Acceptance criteria

Initialization fails with a machine-readable incompatibility diagnostic **and** no undefined compatibility mode.

## Failure disposition

Stop the session **before** registry use **or** Tool dispatch.
