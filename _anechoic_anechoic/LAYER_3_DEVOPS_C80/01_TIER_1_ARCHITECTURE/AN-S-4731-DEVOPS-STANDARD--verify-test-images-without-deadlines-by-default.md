---
atom_family: SPEC
atom_id: AN-S-4731
container:
  component: C80
tier: 1
context:
  template: STANDARD
  lens: DevOps
state:
  status: active
  version: 3
  updated_at: '2026-11-23T14:44:32.013181+00:00'
---

## Summary

Verify test images without deadlines by default

## Claim

### Prose Claim

Verify test images without deadlines by default while the relevant process or job is alive. Allow the operator to abort the active run. Report process exit or job failure explicitly. Record elapsed time separately.

Use `ANECHOIC_TEST_IMAGE_DEADLINES` for test images. Leave it unset or set it
to `0` for deadline-free verification. Set it to `1` to restore test-image
deadlines for diagnostics.

Pass the switch explicitly to the test processes and jobs that use it. Omit
it from production Docker launch environments. Keep production timers in force.
