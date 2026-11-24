---
atom_family: SPEC
atom_id: AN-S-1411
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 3
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Reject duplicate public MCP identities

## Claim

### Prose Claim

Verify that each enabled code-owned registration entry yields one callable MCP identity and duplicate public identities refuse publication.

## Details

Attempt to publish two generated entries with the same public MCP identity. Reject the duplicate identity with an explicit diagnostic and expose neither conflicting entry as current.
