---
atom_family: SPEC
atom_id: AN-S-1402
container:
  component: C21
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 9
  updated_at: 2026-10-24 01:18:03 +0400
---
## Summary

Redact one secret from an MCP result

# Redact one secret from an MCP result

## Claim checked

MCP does **not** expose a secret through a projected capability result **or** diagnostic.

## Test case

Inject one secret-bearing diagnostic value into a Tool result fixture.

## Acceptance criteria

the public MCP representation excludes that value while retaining the classified failure meaning.

## Failure disposition

Stop the affected capability **and** treat the representation as a secret-boundary defect.
