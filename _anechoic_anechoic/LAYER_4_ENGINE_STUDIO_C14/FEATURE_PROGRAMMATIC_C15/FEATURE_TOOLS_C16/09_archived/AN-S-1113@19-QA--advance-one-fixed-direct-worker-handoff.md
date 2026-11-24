---
atom_family: SPEC
atom_id: AN-S-1113
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Advance one fixed direct worker handoff

# Advance one fixed direct worker handoff

## Claim checked

a fixed direct worker handoff advances **only** the transition already declared by
the manager.

## Test case

given a manager-produced two-step execution graph whose second step depends on
the first, execute the first worker **and** its synchronous handoff.

## Acceptance criteria

the exact typed result reaches **only** the declared second worker, the manager is
**not** re-entered for a new decision, **and** neither worker can select **or** alter the
downstream transition.

## Failure disposition

reject the handoff **when** a result reaches an undeclared worker, a worker changes
the transition, the manager is re-entered for an already declared decision, **or**
the handoff loops.

## Sources

- [Python documentation: unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [PEP 544 — Protocols](https://peps.python.org/pep-0544/)
