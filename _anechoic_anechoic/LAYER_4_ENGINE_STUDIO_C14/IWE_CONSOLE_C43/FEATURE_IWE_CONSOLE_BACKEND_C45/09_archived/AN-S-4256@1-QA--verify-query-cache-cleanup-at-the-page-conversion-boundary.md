---
atom_family: SPEC
atom_id: AN-S-4256
container:
  component: C45
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 17:43:47 +0400
---

## Summary

Verify query-cache cleanup at the page-conversion boundary.

## Claim

### Prose Claim

If first-page conversion fails after materialization, QueryStore removes the
generated result table and registration before returning the failure, so no
query ID is exposed for the failed result. If a later page conversion fails
after a query ID is known, the query ID and cache remain available for other
page requests.

## Details

| Fixture | Expected outcome |
| --- | --- |
| First-page conversion of `NaN` or infinity | The request fails without a query ID and leaves no generated result table or registration. |
| Later-page conversion with a known query ID | The page request fails, but the known query ID and materialized cache remain available. |
