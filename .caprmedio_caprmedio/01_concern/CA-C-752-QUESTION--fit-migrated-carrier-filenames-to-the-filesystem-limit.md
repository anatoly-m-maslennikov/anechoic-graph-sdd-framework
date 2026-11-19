---
identity:
  atom_id: CA-C-752
  ref_id: CA-C-752
context:
  container:
    scope_unit: CA-SU-00
  role: concern
  form: Question
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO
  tier: 3
  concern:
    priority: Medium
state:
  status: active
  version: 1
  updated_at: '2026-11-19T02:17:51.687074+00:00'
destination:
  file:
    name: CA-C-752-QUESTION--fit-migrated-carrier-filenames-to-the-filesystem-limit.md
    path: .caprmedio_caprmedio/01_concern
---
## Summary

Fit migrated carrier filenames to the filesystem limit

## Concern

When the complete Summary slug exceeds the filesystem's filename limit,
may the carrier use the longest slug that fits after its required markers?

## Details

The reviewed carrier formula uses the complete Summary slug. The 180
held filenames are 275 to 1,815 bytes against a 255-byte limit.
They cover 176 Archived revisions and four Drafts.

The proposed cutoff preserves the Atom ID, Version and Draft marker
where present, lens, and extension. The full Summary stays in Markdown.
The path receipt keeps the original filename and exact revision alias.

A per-carrier cutoff produced zero case-insensitive path collisions among
these 180 candidates and against the 65,208 rendered destinations in the
tested capture.
