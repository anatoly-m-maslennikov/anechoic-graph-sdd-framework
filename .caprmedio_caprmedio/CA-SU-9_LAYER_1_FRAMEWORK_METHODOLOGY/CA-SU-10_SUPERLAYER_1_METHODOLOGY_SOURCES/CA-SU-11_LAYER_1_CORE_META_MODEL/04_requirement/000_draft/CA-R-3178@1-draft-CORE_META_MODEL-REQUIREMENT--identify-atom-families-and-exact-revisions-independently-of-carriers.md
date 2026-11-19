---
identity:
  atom_id: CA-R-3178
  ref_id: CA-R-3178@1-draft
context:
  container:
    scope_unit: CA-SU-11
  role: requirement
  form: requirement
  topics:
    main_subject: MODEL//CAPRMEDIO <+ Atom
  tier: 3
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:04:42.624158+00:00'
destination:
  file:
    name: CA-R-3178@1-draft-CORE_META_MODEL-REQUIREMENT--identify-atom-families-and-exact-revisions-independently-of-carriers.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Identify Atom families and exact revisions independently of carriers

## Claim

### Prose Claim

An Atom is an independently addressable, versioned contribution. Its ID is <project prefix>-<family>-<number>: S for Spec, T for Ticket, and P for Project Meta. An Atom retains its family. Its ID identifies the Atom independently of its carrier, path, filename, lens, or template suffix. A revision reference identifies the exact Atom and Version, including a Draft qualifier when applicable. Filename suffixes may express a template or lens but are not part of the Atom ID.

## Details

Acceptance: AN-S-123-DECISION and AN-S-123-BACK can be filenames for AN-S-123; changing lens, name, or carrier does not change that ID. AN-S-123@1 and AN-S-123@2 designate different exact revisions of the same Atom. A mapped exact legacy reference resolves to its corresponding revision.
Confirmed separate legacy lineages receive distinct Atom IDs and preserve
their versions. An ambiguous legacy revision reference requires its
original source path. Only Draft status uses the Draft qualifier in
Anechoic. An archived withdrawn Draft uses the ordinary Archived reference.
CA-P-3075 owns the frozen inventory, ID map, and
migration batches.

Sources: CA-A-1462@1-draft, CA-R-2508@15. Task: CA-P-3080.
