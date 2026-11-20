---
identity:
  atom_id: AN-T-2781
context:
  container:
    component: C00
  tier: 3
  template: question
state:
  status: active
  version: 1
  updated_at: '2026-11-19T02:17:51.687074+00:00'
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
