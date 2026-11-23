---
atom_family: SPEC
atom_id: AN-S-1398
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Preserve canonical Tool ownership through one MCP call

# Preserve canonical Tool ownership through one MCP call

## Claim checked

MCP delegates a call **without** reimplementing the canonical Tool's decisions **or** lifecycle behavior.

## Test case

Invoke one exposed Tool with a fixture that would reveal an MCP-side target **or** lifecycle decision.

## Acceptance criteria

**only** the canonical Tool performs that decision **and** MCP returns its resulting structured outcome unchanged.

## Failure disposition

Reject the transport implementation as an unauthorized second operation owner.
