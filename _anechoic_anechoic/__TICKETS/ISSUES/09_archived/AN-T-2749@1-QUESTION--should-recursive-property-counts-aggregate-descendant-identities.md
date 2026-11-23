---
atom_family: TKT
atom_id: AN-T-2749
container:
  component: C9
priority: 2
context:
  template: question
state:
  status: archived
  version: 1
  updated_at: 2026-11-02 08:06:47 +0400
---

## Summary

Should recursive Property counts aggregate descendant identities?

## Claim

The selected default is that `p.**[name format]{:n}` counts the aggregate of
selected distinct descendant Property identities below p within each bearer.

## Details

Context: the prior language named recursive counts without choosing between an
aggregate and a per-recursive-parent interpretation. Decision: use aggregate
selection because `**` selects descendants across depths and Property names are
unique among siblings. Blast radius: validation of nested Property declarations;
direct-value counts and immediate-child counts remain separate. Question for
future change only: is a distinct per-recursive-parent operator needed?
