---
atom_family: SPEC
atom_id: AN-S-1530
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 21
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Reject unknown lifecycle directory

# Reject unknown lifecycle directory

## Test case

**Fixture:** add a lifecycle directory whose Status is **not** admitted by the complete qualified Content Role **and** Type path of its owning Atoms. include a directory admitted by that exact path as a control; do **not** substitute a universal Content Role-only Status domain.

**Expected result:** fail the unregistered lifecycle directory with the stable unknown-lifecycle-directory diagnostic **and** a non-zero exit. do **not** reject the admitted control on this domain check; retain its other applicable placement rules.
