---
atom_family: SPEC
atom_id: AN-S-1914
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: draft
  version: 24
  updated_at: '2026-11-14T08:28:16.789841+00:00'
---
## Summary

Bound and control MCP requests

## Claim

### Prose Claim

Before Tool dispatch, validate every admitted MCP message against its schema and set declared time and resource bounds.
MCP supports cancellation and reports progress only for admitted long-running operations.
Each request has an explicit admission and completion boundary.

## Details

- Reject invalid or expired requests before dispatch.
- End invalid, expired, canceled, or resource-exhausted requests with a structured outcome.
  Preserve Tool and Project state and stop ungoverned background work.
