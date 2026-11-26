---
atom_family: TKT
atom_id: AN-T-3965
container:
  atom: AN-T-3904
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-25T13:22:23.895663+00:00"

---

## Summary

Update eDSL engine

## Work

Implement static parsing and validation for the admitted typed Manifest forms. Preserve existing model admission and binding checks. Use the Axiom as the first pilot, including fixed values and one Project container.

Start from the reviewed bundle, then compile and validate one fresh snapshot of active C9 and Project Config Formal Manifests through the existing Model service. Publish the Project’s last good Model only on success. Report failures and retain the prior Model or first-boot bundle.

Expose the accepted Primary and bearer Property trees and the latest candidate findings with attempt and accepted generation context. Maintain `mrt_project_structure` through watcher-triggered atomic ingestion, one row per Component.

## Acceptance

Focused checks admit the pilot, reject invalid declarations, and preserve existing model behavior. Record the compiled result and any unsupported syntax.

Checks cover candidate failure, first boot, both projections, diagnostics, and atomic Structure updates.

## Verification

The typed Node, Property, and Relation checks passed. The Axiom pilot fixes its values and admits one Project target. Signed numeric literals are supported. Arbitrary Python expressions and unreviewed callbacks remain outside the admitted syntax.

Model fingerprint `68b34386b844e36f6a96af171e20c204a4ad6ec355c3b16839b07cb5dd16c766` compiled from the active snapshot. The failure checks retained the accepted Model or loaded the reviewed bundle on first boot. Both Model projections matched SQL, and Structure replacement passed the atomic publication checks.
