---
atom_family: TKT
atom_id: AN-T-2008
structure:
  container:
    component: C45
  priority: 2
context:
  template: problem
state:
  status: resolved
  version: 2
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

First-page conversion failures retain unreachable result tables.

## Concern

When conversion of the first page produced `NaN`, the request failed before a
query ID was returned, but the generated result table remained cached. That
leaked disposable query state for a result the caller could not address.

## Resolution

QueryStore now drops the generated result before propagating a first-page
conversion error. A later page-conversion failure with a known query ID keeps
that cache and ID available for other pages. `tests/test_query_store.py` passes
9 tests, including the `NaN` regression. This resolves the source defect;
runtime adoption and deployment remain separate tracking concerns.
