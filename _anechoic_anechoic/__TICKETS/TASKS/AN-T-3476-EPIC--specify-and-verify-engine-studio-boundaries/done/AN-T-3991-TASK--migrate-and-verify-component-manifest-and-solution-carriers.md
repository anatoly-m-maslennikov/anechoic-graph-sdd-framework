---
atom_family: TKT
atom_id: AN-T-3991
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-27T03:05:33.417273+00:00"
---
## Summary

Migrate and verify Component Manifest and Solution carriers

## Acceptance

Reconcile selected Spec Engine carriers when the change resolves a
confirmed mismatch or gives a useful regression case. Put the public
Contract in the Tier 1 Manifest. Link its Tier 0 Solution directly with
ANSWERS. Preserve source history.

Use the C85 provenance, C86 bounded framing, or C89 rejection findings
to select the revisions worth changing. Bulk migration of Component and
Component Seed carriers is outside this task.

## Verification

Migrated 65 Component Manifests and embedded all 39 Active Component Contracts locally. Archived the standalone Active carriers after embedding. The lifecycle rejects standalone creation, revision, publication, and activation. Archival remains available. Solution pins still need reconciliation.
