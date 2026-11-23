---
atom_family: SPEC
atom_id: AN-S-1294
container:
  component: C15
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 22
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Reject unchecked cyclomatic complexity

# Reject unchecked cyclomatic complexity

## Claim checked

**every** new **or** materially changed executable unit has a result from the admitted
cyclomatic-complexity lint **and** stays within its Evaluation-owned maximum **or** one
accepted bounded exception.

## Test case

evaluate one materially changed function for which no current complexity-lint
result exists.

## Acceptance criteria

pass **only** **when** conformance is rejected **until** **all** of the following hold:

- the admitted lint reports a value for the changed unit.
- that value satisfies the Evaluation-owned maximum **or** an accepted bounded exception covers that value.

## Failure disposition

block the changed unit from claiming source-boundary conformance.

## Sources

- [CA-M-419 — Ratchet hand-authored Python source boundaries](../05_method/CA-M-419-PROGRAMMATIC-ENG_POLICY--ratchet-hand-authored-python-source-boundaries.md)
- [CA-M-420 — Ratchet typing and automation adoption](../05_method/CA-M-420-PROGRAMMATIC-ENG_POLICY--ratchet-typing-and-automation-adoption.md)
