---
atom_family: TKT
atom_id: AN-T-4088
container:
  atom: AN-T-4087
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: '2026-11-28T09:23:17.312328+00:00'
---
## Summary

Clear the v0.5.0 Static and Code Access blockers

## Work

Close the release-blocking findings in AN-T-4065 and AN-T-4067.
Resolve the denied imports in AN-T-3978 at their owning Package
entries and Active Manifests. Keep test access grants local to tests.

The Operator deferred 79-character source width. Keep the findings in
AN-T-4065. Run the other Static checks, including 45/300.

## Acceptance

AN-T-4068 has a passing full-checkout Static and Realization Graph
receipt in the locked environment. It records the Git revision and
exact Model and Manifest pins. All required Static checks pass.

Require zero denials, undeclared bypasses, and production imports from
Test Packages. Record the disposition of uncertain imports. Reuse
the exact receipt in the candidate gate when its inputs match.

## Progress

Sealed source `cd302fd070cd16e9c82812350fe5a9d6cc287187`
passed the locked Static gate and all 53 Static tests. Source width
is deferred as recorded in AN-T-4065. Bytecode remains inside the
Project temporary boundary.

The Realization Graph found zero denials, undeclared bypasses, and
production imports from Test Packages. Of 26 uncertain imports,
24 are fixture launch imports and two are C30 standalone reader
fallbacks. Lean validated Model
`dc0e1f83226a3d5f7ff259d3856d7b72836f262f17616b56c099ad75dbba5c04`.

Retained evidence is in `v050-final-static.log` and
`v050-final-graph-receipt.json`. Both use the same source seal.
