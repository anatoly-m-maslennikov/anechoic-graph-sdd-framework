---
atom_family: SPEC
atom_id: AN-S-3884
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 9
  updated_at: 2026-10-24 01:18:03 +0400
---
## Summary

Reject duplicate MCP projection of one Tool unit

# Reject duplicate MCP projection of one Tool unit

## Claim checked

One validated immediate Tool unit yields exactly one callable MCP identity.

## Test case

Attempt **to** publish two callable MCP identities from one valid source Tool.

## Acceptance criteria

Publication fails with a duplicate-projection diagnostic **and** exposes neither alias as current.

## Failure disposition

Stop registry publication **until** the one-to-one mapping is restored.
