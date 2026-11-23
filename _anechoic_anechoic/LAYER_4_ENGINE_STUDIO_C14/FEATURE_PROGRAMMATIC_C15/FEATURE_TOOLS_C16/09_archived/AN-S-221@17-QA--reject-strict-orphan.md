---
atom_family: SPEC
atom_id: AN-S-221
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 17
  updated_at: 2026-10-24 02:04:43 +0400
---
## Summary

Reject strict orphan

# Reject strict orphan

## Test case

**Fixture:** leave an Active non-Goal tier-classified RMED Atom parentless **in** a strict scope, with its applicable Type **not** registered as orphan-permitted under CA-R-037. include a permitted orphan Type as a control.

**Expected result:** fail the non-exempt fixture with the stable strict-orphan diagnostic **and** a non-zero exit; do **not** reject the registered orphan-permitted control for parentlessness alone. this verdict diagnoses conformance **without** mutating the Atom, inventing a parent, **or** overriding the Operator's permission **to** retain a nonconforming Artifact.
