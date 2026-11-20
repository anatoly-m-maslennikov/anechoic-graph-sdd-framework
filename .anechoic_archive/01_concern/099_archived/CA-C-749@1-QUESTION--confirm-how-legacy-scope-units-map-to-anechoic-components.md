---
identity:
  atom_id: CA-C-749
  ref_id: CA-C-749@1
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
  updated_at: '2026-11-19T00:00:41.374423+00:00'
destination:
  file:
    name: CA-C-749@1-QUESTION--confirm-how-legacy-scope-units-map-to-anechoic-components.md
    path: .anechoic_anechoic/01_concern/099_archived
---
## Summary

Confirm how legacy Scope Units map to Anechoic Components

## Concern

Which legacy Component IDs and parent relationships should the migration
use for the approved Anechoic topology?

## Details

CA-A-1461 specifies three direct children of Anechoic. The legacy Project
has seven. CA-P-3073 owns the target name, ID, and parent inventory.
CA-P-3075 needs that inventory before assigning physical SPEC destinations.

Preserve existing Component IDs and internal parent relationships where
the approved topology permits. Confirm the former top-level branches
that need a new parent or an explicit retirement disposition. The
Methodology Atom batch targets Meta-ontology under CA-P-3078.

CA-P-3092 can continue inventory and reference reconciliation while
these target placements remain open.
