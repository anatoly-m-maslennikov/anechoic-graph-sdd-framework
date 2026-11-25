---
atom_family: TKT
atom_id: AN-T-3471
container:
  atom: AN-T-3468
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: '2026-11-23T23:07:47.000000+00:00'
---
## Summary

Check findings from the carrier body Adapter pilot

## Work

After AN-T-3470, compare the Solution model and source-derived model in
Lean. Verify reported behavior against the actual Python entry points in the
scoped `carrier_body__pub.py` module. Use pinned Python and Code Analysis as
implementation-side evidence.

Compare the exact pinned symbols `frontmatter_bounds` and `source_body`, with
their source revision and locations recorded as binding evidence. Compare
findings with the boundaries declared by AN-T-3469.

## Acceptance

Check LF, CRLF, empty frontmatter, missing delimiters, and exact body bytes.
Record each confirmed mismatch with its input and source location. Record
any unresolved coverage and state when the checks found no mismatch.
Record gaps when the current model lacks formal boundary notation.
