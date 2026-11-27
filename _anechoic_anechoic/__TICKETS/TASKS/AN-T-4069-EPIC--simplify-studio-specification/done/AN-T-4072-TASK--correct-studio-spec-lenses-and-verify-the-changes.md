---
atom_family: TKT
atom_id: AN-T-4072
container:
  atom: AN-T-4069
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: "2026-11-27T14:51:20+00:00"
---

## Summary

Correct Studio Spec Lenses and verify the changes

## Acceptance

Check Current Studio Lens assignments against Component
Manifests and the meaning of each changed claim. Fix
confirmed mismatches. Verify affected bindings, Model and
Structure admission, and selected formal checks.

## Evidence

AN-S-476 and AN-S-463 now use DevOps, with their claim
bodies intact. The scope matcher accepted all 1,218 checked
Current carriers with explicit Lens whitelists.

Model and Structure admission passed. Focused formal tests
passed. The whole-Model Lean timeout is recorded in the Epic.
