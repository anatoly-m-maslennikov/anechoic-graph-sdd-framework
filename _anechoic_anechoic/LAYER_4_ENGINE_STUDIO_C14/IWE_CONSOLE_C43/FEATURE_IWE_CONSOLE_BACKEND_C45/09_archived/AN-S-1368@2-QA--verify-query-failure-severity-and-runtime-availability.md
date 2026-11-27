---
atom_family: SPEC
atom_id: AN-S-1368
container:
  component: C45
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-11-09 00:09:26 +0400
---

## Summary

Verify query-failure severity and runtime availability.

## Claim

### Prose Claim

An invalid SQL statement or invalid query argument is a failed request with a
`query_error` diagnostic at `WARNING` severity and outcome `failed`; the
healthy Workbench owner remains usable. A genuine Workbench-unavailable or
unexpected runtime failure remains `ERROR` with outcome `blocked` and keeps its
restart-required or runtime-failure boundary.

## Details

| Fixture | Expected outcome |
| --- | --- |
| Invalid SQL or query arguments | Return the useful request error, log `query_error` as `WARNING`, mark the outcome `failed`, and keep the owner available. |
| Workbench-unavailable or unexpected runtime failure | Log `ERROR`, mark the outcome `blocked`, and preserve the runtime failure boundary. |
| Valid request after an invalid request | The native MCP/HTTP path continues and the valid request succeeds. |
