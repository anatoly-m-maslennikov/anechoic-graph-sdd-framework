---
identity:
  atom_id: CA-C-750
  ref_id: CA-C-750@1
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
  status: archived
  version: 1
  updated_at: '2026-11-19T00:45:31.529847+00:00'
destination:
  file:
    name: CA-C-750@1-QUESTION--resolve-exact-revision-collisions-from-withdrawn-drafts.md
    path: .anechoic_anechoic/01_concern/099_archived
---
## Summary

Resolve exact revision collisions from withdrawn Drafts

## Concern

How should migration preserve a withdrawn Draft when an ordinary
revision of the same Atom already has its Version?

## Details

The inventory finds eight conflicts after normalizing withdrawn Drafts
to Archived. Seven pairs have different Markdown bodies. Two pairs
include a Current revision. CA-I-9@2 is one example.

Keep the ordinary revision in its lineage. One option is to assign the
withdrawn carrier its own Archived ID and keep its original exact pin
and path in the migration map. This preserves both Versions and bodies.
CA-P-3092 holds these collisions pending a decision.