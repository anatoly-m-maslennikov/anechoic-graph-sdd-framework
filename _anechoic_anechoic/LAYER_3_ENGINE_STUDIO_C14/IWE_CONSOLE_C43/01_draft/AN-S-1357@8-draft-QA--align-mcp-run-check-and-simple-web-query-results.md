---
atom_family: SPEC
atom_id: AN-S-1357
container:
  component: C43
tier: 5
context:
  lens: QA
state:
  status: draft
  version: 8
  updated_at: '2026-11-14T07:52:52.827355+00:00'
---
## Summary

Align MCP Run, Check, and simple web query results

## Claim

### Prose Claim

Verify MCP and web Run, Page, and Check return equivalent results through
the same synchronous query capability.

## Details

- Compare complete default exports and explicit inline pages. Preserve
  ordered duplicate columns, Unicode, exact counts, and positional values.
- A Run executes once. After source refresh, its query ID still returns
  the same pages. A new Run reads refreshed data.
- Check returns validation metadata and available exact counts. It returns
  no rows or file and creates no save or log entry. Responses omit SQL echoes.
- Invalid SQL, size, offset, or query ID returns a useful error without retry.
- Exercise both adapters with the optional UI absent, and check the production
  web editor, errors, counts, and paging through the Python listener.
- Verify that the frontend fetches one page at a time and uses shared controls.
- Source errors report their path to stderr. Unrelated valid data stays queryable.
