---
identity:
  atom_id: AN-S-1948
context:
  container:
    component: C43
  tier: 5
  lens: DevOps
state:
  status: active
  version: 3
  updated_at: '2026-11-12T01:42:31.971586+00:00'
---

## Summary

Deliver query-visible audit tables

## Claim

### Prose Claim

Deliver these stable SQL tables through the shared Workbench backend and the existing `query_run` and `query_page` interfaces:

- `atom_parse_issues`
- `atom_schema_issues`
- `atom_declared_carrier_issues`
- `atom_physical_carrier_issues`
- `atom_duplicate_revision_issues`

Each table has only these columns: `reference` (nullable), `relative_path`, `filename`, `issue_category`, `property` (nullable), `observed` (nullable), `expected` (nullable), and `diagnostic`. HTTP and MCP must use the same backend and these exact names. Expose these table and column names through query_schema. Existing model-driven Atom Header/Content schema generation and invalid-Declaration handling remain in force. Publish audit rows after source rows commit, and report `audits_pending` and `last_audit_ms` through `workbench_status` and its web equivalent. A pending audit does not prevent queries or lifecycle responses. Audits leave source files unchanged.

