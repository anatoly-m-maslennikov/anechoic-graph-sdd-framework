---
atom_family: SPEC
atom_id: AN-S-1401
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 12
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Rebuild one unchanged MCP registry identically

# Rebuild one unchanged MCP registry identically

## Claim checked

Repeated MCP registry generation over one unchanged sealed frontier is semantically idempotent.

## Test case

Generate the registry twice from the same Tool-contract **and** project frontier.

## Acceptance criteria

the two registries have the same capability identities **and** schemas; volatile execution metadata does **not** change that result.

## Failure disposition

Stop publication **and** report the first nondeterministic source **or** ordering defect.
