---
atom_family: TKT
atom_id: AN-T-4094
container:
  atom: AN-T-4087
priority: 2
context:
  template: task
  label: Task
relations:
  IS_BLOCKED_BY:
  - AN-T-4088
  - AN-T-4089
  - AN-T-4090
  - AN-T-4091
  - AN-T-4092
  - AN-T-4093
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-28T08:08:02+00:00'
---
## Summary

Publish and verify v0.5.0

## Work

Present the reviewed PR and all passing candidate receipts for the
Operator's publication decision. Publish through the existing public
workflow.

## Acceptance

Record the PR URL, exact published main commit, public version, and
verified build or image identity. Check the published setup entry
point and first Project smoke. Close the Epic after these checks pass.

## Publisher verification

The prior GitHub release workflow invokes the removed `dset_toolchain`
module. The corrected workflow reads the current version contract.
It verifies the protected merge tree against the reviewed PR head
before emitting tag and release inputs.

The local replay passed five cases. It emits `v0.5.0` for a new
version, skips an unchanged version, and refuses an invalid version,
different merge tree, or wrong branch. GitHub publication is pending.

The version check also accepted the protected merge replay for exact
head `a99d4b49` and selected tag `v0.5.0`.
