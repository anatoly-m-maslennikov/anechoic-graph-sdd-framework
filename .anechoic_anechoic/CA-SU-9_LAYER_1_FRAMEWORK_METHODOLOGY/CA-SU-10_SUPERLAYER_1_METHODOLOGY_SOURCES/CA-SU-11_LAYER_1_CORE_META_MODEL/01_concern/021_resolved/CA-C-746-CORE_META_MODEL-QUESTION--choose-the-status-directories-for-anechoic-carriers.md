---
identity:
  atom_id: CA-C-746
  ref_id: CA-C-746
context:
  container:
    scope_unit: CA-SU-11
  role: concern
  form: Question
  topics:
    main_subject: MODEL//ANECHOIC <+ Atom
  tier: 3
  concern:
    priority: Medium
state:
  status: resolved
  version: 1
  updated_at: '2026-11-18T22:11:00.425054+00:00'
destination:
  file:
    name: CA-C-746-CORE_META_MODEL-QUESTION--choose-the-status-directories-for-anechoic-carriers.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/01_concern/021_resolved
---
## Summary

Choose the status directories for Anechoic carriers

## Concern

The new model defines four logical trees and versioned carrier filenames.
It needs a final physical destination for Draft, Current, and Archived
carriers within SPEC, PMETA, and TKT.

## Details

Use exact references and filename markers in the candidate model, and
validate logical tree membership. Keep the current placement principle as
the starting point for migration planning: shared Draft and Archived
directories and Current records local to their container. Confirm which
new roots own the shared directories and how Current folders are named.

Affected work is CA-P-3087 under CA-P-3074. Migration remains CA-P-3075.
