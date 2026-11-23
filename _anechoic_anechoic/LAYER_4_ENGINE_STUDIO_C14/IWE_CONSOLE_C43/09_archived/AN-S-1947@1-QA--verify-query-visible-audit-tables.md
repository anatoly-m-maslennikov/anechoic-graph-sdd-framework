---
atom_family: SPEC
atom_id: AN-S-1947
container:
  component: C43
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-11-11 00:34:40 +0400
---

## Summary

Verify query-visible audit tables

## Claim

### Prose Claim

Using the real Workbench backend and both query interfaces, verify that:

- each of the three audit cases has positive and negative examples for both Current and Draft sources;
- readable Current and Draft Atoms with no issue produce no audit row;
- each inaccessible source produces `issue_category = query_inaccessible_atom`, each declared carrier conflict produces `issue_category = declared_carrier_inconsistency`, and each physical carrier mismatch produces `issue_category = physical_carrier_mismatch`, with source identity or path, diagnostic and observed or expected values in the appropriate columns;
- an invalid or unreadable source is reported without a normal Atom row, valid sources remain queryable, and source files remain unchanged;
- `query_run` and `query_page` return the same audit rows through HTTP and MCP.

