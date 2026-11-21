---
atom_family: SPEC
atom_id: AN-S-1947
container:
  component: C43
tier: 6
context:
  lens: QA
state:
  status: draft
  version: 3
  updated_at: '2026-11-14T07:53:38.798834+00:00'
---
## Summary

Verify query-visible audit tables

## Claim

### Prose Claim

Verify archive selection and query-visible diagnostics through the real
Workbench backend.

## Details

- Cold start exposes Current, Draft, and Backlog. Load two Archive Scope Unit
  and Role pairs. Verify scoped coverage and repeat loading without duplicates.
- Distinguish unloaded history from absent revisions. ID and Version allocation
  accounts for unloaded Archives. Lifecycle can read a newly archived exact file.
- Verify all five issue types from CA-D-715. Parseable files stay queryable,
  Draft and Backlog stay out of duplicate checks, and source bytes are preserved.
- Delayed audits leave committed rows and lifecycle responses available.
  Verify elapsed time, latest diagnostics, and HTTP/MCP parity.
