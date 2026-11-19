---
identity:
  atom_id: CA-C-750
  ref_id: CA-C-750
context:
  container:
    scope_unit: CA-SU-00
  role: concern
  form: Question
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC
  tier: 3
  concern:
    priority: Medium
state:
  status: resolved
  version: 2
  updated_at: '2026-11-19T00:58:05.892945+00:00'
destination:
  file:
    name: CA-C-750-QUESTION--resolve-exact-revision-collisions-from-withdrawn-drafts.md
    path: .anechoic_anechoic/01_concern/021_resolved
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