---
identity:
  atom_id: AN-P-70
context:
  container:
    component: C9
  tier: 3
state:
  status: draft
  version: 22
  updated_at: '2026-11-13T08:54:51.061268+00:00'
---
## Summary

Persist Atom replacement through ordered Carrier transitions

## Operation

Persist an accepted Atom replacement by resolving every distinct `IS_REPLACEMENT_FOR` target, including targets with different IDs and many-to-one replacement. Before publishing the Draft as Current, archive each eligible Current target once and skip every target already Archived, including one archived by composed Update. Archival preserves each target's Version and Updated At. Then publish the Draft with the supplied allowed Current Status and remove its Draft carrier. Use the publication Version required by CA-R-1432. Derive carrier filename and location from the model.

Record actual business observations in the Journal independently; recording failure does not block the lifecycle effect. Stop on an effect failure and report completed and incomplete effects without retry, rollback, recovery or repair.
