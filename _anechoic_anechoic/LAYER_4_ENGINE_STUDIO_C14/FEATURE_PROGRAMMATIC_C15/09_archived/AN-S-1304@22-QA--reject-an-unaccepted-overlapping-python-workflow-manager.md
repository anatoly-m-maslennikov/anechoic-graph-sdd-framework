---
atom_family: SPEC
atom_id: AN-S-1304
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 22
  updated_at: 2026-10-27 19:59:34 +0400
---
## Summary

Reject an unaccepted overlapping Python workflow manager

## Claim

### Prose Claim

#### Claim checked

one Python workflow does **not** mix uv with another overlapping environment **or**
dependency manager **unless** an accepted Method owns a bounded exception.

#### Test case

evaluate one governed path that runs both uv **and** Poetry **without** an accepted
exception.

#### Acceptance criteria

pass **only** **when** the path is rejected **before** environment mutation.

#### Failure disposition

block the alternative manager **until** a required capability, bounded carriers,
commands, cost, recovery procedure, **and** Operator acceptance are governed.

#### Sources

- [CA-M-429 — Use uv as the default Python workflow frontend](../05_method/CA-M-429-PROGRAMMATIC-ENG_POLICY--use-uv-as-the-default-python-workflow-frontend.md)
