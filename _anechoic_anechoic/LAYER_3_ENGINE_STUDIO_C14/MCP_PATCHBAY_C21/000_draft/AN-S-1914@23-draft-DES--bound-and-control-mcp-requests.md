---
atom_family: SPEC
atom_id: AN-S-1914
structure:
  container:
    component: C21
  tier: 1
context:
  lens: DES
state:
  status: draft
  version: 23
  updated_at: '2026-11-14T08:20:17.954130+00:00'
---
## Summary

Bound and control MCP requests

## Claim

### Prose Claim

MCP must validate each request before dispatch, apply declared time and resource
bounds, and report progress only for admitted long-running work. Invalid, expired,
canceled, and exhausted requests end with a structured outcome.

## Details

- Reject invalid or expired requests before dispatch. Validate messages
  against the admitted protocol schema.
- Support cancellation. Preserve Tool and Project state on termination
  and leave no ungoverned background work.

### Sources

- [MCP base protocol](https://modelcontextprotocol.io/specification/2025-06-18/basic/index)
  and [MCP tasks](https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/tasks).
- [CA-A-057](../../../02_analysis_and_advisory/CA-A-057-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-programmatic-specialization-authority.md).
