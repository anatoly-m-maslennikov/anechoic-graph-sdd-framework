---
atom_family: SPEC
atom_id: AN-S-1292
container:
  component: C15
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 22
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject an oversized changed Python file

## Claim

### Prose Claim

#### Claim checked

one new **or** materially changed hand-authored PROGRAMMATIC Python file remains at
**or** below 200 physical lines **or** has a specific bounded exception.

#### Test case

evaluate one changed 201-line hand-authored Python file with no file-size
exception.

#### Acceptance criteria

pass **only** **when** conformance is rejected **until** the file is reduced, split by
responsibility, **or** supplied with one accepted bounded exception.

#### Failure disposition

block the changed file from claiming source-boundary conformance.

#### Sources

- [CA-M-419 — Ratchet hand-authored Python source boundaries](../05_method/CA-M-419-PROGRAMMATIC-ENG_POLICY--ratchet-hand-authored-python-source-boundaries.md)
