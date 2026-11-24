---
atom_family: SPEC
atom_id: AN-S-1521
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 17
  updated_at: 2026-10-27 19:59:28 +0400
---
## Summary

Reject RMED subject cardinality

# Reject RMED subject cardinality

## Test case

- give an RMED Atom **`=0`** GOVERNS targets.
- give another RMED Atom **`>=2`** distinct GOVERNS targets.
- give a valid RMED Atom **`=1`** GOVERNS target **and** **`>=0`** unique DEPENDS_ON targets; include a case with **`>=2`** DEPENDS_ON targets.

## Expected result

reject the first two fixtures with the stable RMED-subject-cardinality diagnostic **and** a non-zero exit. accept the third fixture with respect **to** Subject cardinality. count **only** GOVERNS targets toward the **`=1`** governed-target constraint; DEPENDS_ON targets **must not** be counted as additional GOVERNS targets.
