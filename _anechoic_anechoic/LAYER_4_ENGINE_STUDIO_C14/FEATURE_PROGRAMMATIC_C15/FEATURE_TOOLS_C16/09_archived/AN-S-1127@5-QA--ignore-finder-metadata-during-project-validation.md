---
atom_family: SPEC
atom_id: AN-S-1127
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Ignore Finder metadata during project validation

# Ignore Finder metadata during project validation

## Test case

**Fixture:** compare **otherwise** identical, conforming Project fixtures with **and** **without** a `.DS_Store` entry under the control root.

**Expected result:** exclude `.DS_Store` from governed-Artifact validation **and** return the same governance diagnostics **and** exit status for both fixtures. do **not** emit non-governed-control-root-file solely for that entry, treat it as authority, **or** modify **or** delete it. other selected files remain subject **to** their applicable checks.
