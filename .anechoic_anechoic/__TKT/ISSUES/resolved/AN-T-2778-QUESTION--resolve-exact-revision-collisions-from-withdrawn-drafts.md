---
atom_family: TKT
atom_id: AN-T-2778
structure:
  container:
    component: C00
  priority: 2
context:
  template: question
state:
  status: resolved
  version: 2
  updated_at: '2026-11-19T00:58:05.892945+00:00'
---
## Summary

Resolve exact revision collisions from withdrawn Drafts

## Concern

How should migration preserve a withdrawn Draft when an ordinary
revision of the same Atom already has its Version?

## Details

Give every conflicting withdrawn Draft a separate Archived ID. Keep its
stored Version, original path, and `-draft` alias. Keep the ordinary
revision in its lineage. Apply this rule to each matching collision.

CA-P-3075 records the decision. The allocation rehearsal verified 112
source carriers across eight affected identities. Each exact ordinary
reference and each exact withdrawn Draft reference retained a unique
target. Unrelated lineage ambiguity stays held for review.