---
atom_family: SPEC
atom_id: AN-S-1529
structure:
  container:
    component: C16
  tier: 2
context:
  lens: QA
state:
  status: active
  version: 21
  updated_at: 2026-10-27 19:59:28 +0400
---
## Summary

Reject inactive relation target

# Reject inactive relation target

## Test case

**Fixture:** point a direct Relation authored by an Active RMED Atom at an Archived RMED Atom under ANECHOIC-GOV-REQU-767. also include an admitted Task dependency on a Done prerequisite Task as a control outside the RMED-to-RMED restriction.

**Expected result:** fail the Active RMED-to-Archived RMED fixture with the stable inactive-relation-target diagnostic **and** a non-zero exit. accept the admitted Done prerequisite with respect **to** this restriction; retain **all** other applicable Relation constraints under ANECHOIC-GOV-EVAL-005.
