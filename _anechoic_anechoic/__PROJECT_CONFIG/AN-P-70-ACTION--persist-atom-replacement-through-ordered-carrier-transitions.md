---
atom_family: PROJECT_CONFIG
atom_id: AN-P-70
structure:
  container:
    component: C9
context:
  template: action
state:
  status: active
  version: 21
  updated_at: 2026-10-27 19:59:44 +0400
---
# Summary

Persist Atom replacement through ordered Carrier transitions

## Operation

Persist an accepted Atom replacement by resolving every distinct `IS_REPLACEMENT_FOR` target, including targets with different IDs and many-to-one replacement. Before publishing the Draft as Current, archive each eligible Current target once and skip every target already Archived, including one archived by composed Update. Archival preserves each target's Version and Updated At. Then publish the Draft with the supplied allowed Current Status and remove its Draft carrier. A changed Summary or Content Role creates a new identity promoted at Version 1; otherwise retain the Draft Version without a further increment. Derive carrier filename and location from the model.

Record actual business observations in the Journal independently; recording failure does not block the lifecycle effect. Stop on an effect failure and report completed and incomplete effects without retry, rollback, recovery or repair.
