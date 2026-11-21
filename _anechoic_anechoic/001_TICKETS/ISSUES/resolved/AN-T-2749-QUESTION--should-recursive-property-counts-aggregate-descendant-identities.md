---
atom_family: TKT
atom_id: AN-T-2749
container:
  component: C9
priority: 2
context:
  template: question
state:
  status: resolved
  version: 3
  updated_at: 2026-11-02 14:59:48 +0400
---

## Summary

Should recursive Property counts aggregate descendant identities?

## Question

Does `p.**[name format]{:n}` count all selected descendant Properties together across every depth?

## Details

Resolved by the Operator on 2 November 2026.

- `p.**` selects all descendant Properties recursively.
- `p.*` selects immediate Properties.
- Selectors compose: `p.*.*` selects depth 2; `p.*.**` selects depth 2 and deeper.

The existing aggregate-count rule is confirmed. CA-R-2472 records selector composition.
