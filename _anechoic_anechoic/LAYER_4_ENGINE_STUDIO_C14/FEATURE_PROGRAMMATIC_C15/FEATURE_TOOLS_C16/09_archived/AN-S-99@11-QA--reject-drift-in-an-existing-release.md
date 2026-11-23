---
atom_family: SPEC
atom_id: AN-S-99
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 11
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Reject drift in an existing release

# Reject drift in an existing release

## Claim checked

An existing content-addressed release cannot be reused **or** repaired **in** place **after** **any** installed byte **or** executable mode drifts.

## Test case

Install one release, change one installed registry byte, record the current manifest **and** managed Hook bytes, **and** apply the unchanged canonical source again.

## Acceptance criteria

Installation returns one stable release-collision diagnostic **before** selecting **or** repairing the release. The changed installed byte remains observable, while the current manifest, launchers, Hooks, Git configuration, canonical source, runtime, index, **and** refs remain unchanged.

## Failure disposition

Reject delivery **if** reinstall silently trusts, overwrites, **or** partially repairs the drifted release; repoints **any** managed carrier; **or** changes unrelated state.
