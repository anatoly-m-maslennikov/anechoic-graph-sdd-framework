---
atom_family: TKT
atom_id: AN-T-2784
structure:
  container:
    component: C00
  priority: 2
context:
  template: question
state:
  status: "resolved"
  version: 1
  updated_at: "2026-11-21T00:56:18.270294+00:00"
---
## Summary

Fill empty archive Summaries during migration

## Concern

May migration copy a following legacy H1 title into an existing empty
Summary while preserving every original Markdown byte?

## Details

66 archived carriers begin with an empty `# Summary` followed by a
legacy H1 title. The approved no-Summary repair would prepend a
second Summary and fail strict parsing on every carrier.

In-memory checks passed for all 66 when the exact title was inserted
into the existing section. Removing the insertion restores the
original bytes. The proposed conversion keeps the original title
and all subsequent Markdown, with the insertion recorded in the
migration receipt.
