---
atom_family: SPEC
atom_id: AN-S-1316
container:
  component: C15
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 01:28:26 +0400
---
## Summary

Require a declared benefit for one new Python idiom

# Require a declared benefit for one new Python idiom

## Claim checked

a runtime-dependent Python idiom is admitted **only** for a named benefit inside
the supported boundary.

## Test case

replace an immediate trusted f-string with a t-string while providing no
interpolation processor **or** other correctness, clarity, safety, **or** measured
performance benefit.

## Acceptance criteria

pass **only** **when** the change is rejected **and** the simpler supported idiom remains.

## Failure disposition

reject novelty alone as a benefit **and** return the selection **to** CA-M-406.

## Sources

- [PEP 750 — Template Strings](https://peps.python.org/pep-0750/)
- [CA-M-406 — Adopt current Python idioms only for declared benefit](../05_method/CA-M-406-PROGRAMMATIC-STANDARD-ENG_POLICY--adopt-current-python-idioms-only-for-declared-benefit.md)
