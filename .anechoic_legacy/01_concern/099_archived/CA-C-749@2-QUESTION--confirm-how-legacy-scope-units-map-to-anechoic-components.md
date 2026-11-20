---
identity:
  atom_id: CA-C-749
  ref_id: CA-C-749@2
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
  version: 2
  updated_at: '2026-11-19T00:50:03.097266+00:00'
destination:
  file:
    name: CA-C-749@2-QUESTION--confirm-how-legacy-scope-units-map-to-anechoic-components.md
    path: .anechoic_anechoic/01_concern/099_archived
---
## Summary

Confirm how legacy Scope Units map to Anechoic Components

## Concern

Confirm the remaining Component IDs, parents, and physical paths before
freezing the migration map.

## Details

The Operator confirmed five direct children of Anechoic. Meta-ontology,
Meta-methodology, and Engine Studio are joined by Framework Delivery
(C27) and Operator Documentation (C25).

Retire Community Extensions (C28), Core Extensions (C26), and Field (C29)
as Components. Migrate their 353 inventoried records under Project C00
with their revision histories. Remap any authored Atom containers through
the shared migration map.

CA-P-3073 owns the final name and path inventory. CA-P-3078 routes the
initial Methodology batch to Meta-ontology. CA-P-3092 can continue
inventory and reference reconciliation.