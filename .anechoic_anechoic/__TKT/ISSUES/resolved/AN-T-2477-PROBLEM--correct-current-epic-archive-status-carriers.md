---
identity:
  atom_id: AN-T-2477
context:
  container:
    component: C9
  template: problem
state:
  status: resolved
  version: 2
  updated_at: 2026-10-23 03:14:50 +0400
---
# Summary

Correct current Epic archive Status carriers

## Concern

Six whole prior Workflow Revision snapshots newly retained for this Epic still explicitly carried Active despite their non-current archive placement: O010@7/@8, O011@10/@11 and O015@6/@7. This conflicts with their actual prior-Revision disposition and can misrepresent active source authority. The issue is bounded to these six files; it does not establish a defect in older history or current definitions.

## Evidences

P1478 captured each complete pre-edit carrier, found its unique explicit Active Status and matching @version basename, then changed only Status to Archived and Updated At to the actual 2026-10-04 17:55:44 +0000 edit instant. R1419v9 admits Archived for prior Revisions; R1788v1 requires actual Updated At for every accepted carrier edit; R1432v9/O067v6 retain identity and Version for carrier_only recoding; D289v12 preserves the @version basename and D270v13 governs timestamp serialization.

The saved complete before/after comparison, exact six basenames, former timestamps, byte lengths and full SHA-256 values are retained in physical Done P1478. All six full successor strings exactly equal their captured predecessors after only those two permitted frontmatter replacements. Every other byte is preserved, including Summary, body, identity, Version and other metadata.

## Blast radius

### Disposition

Resolved by the exact six-carrier correction and complete byte comparison in P1478. No current Workflow/Step source, older pre-Epic archive, implementation, source generation or runtime behavior was changed or accepted. Root retains source-stage and dependent-gate authority; this narrow Concern does not close those stages.
