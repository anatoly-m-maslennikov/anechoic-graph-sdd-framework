---
atom_family: SPEC
atom_id: AN-S-1306
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

Verify changed Python with Mypy

# Verify changed Python with Mypy

## Claim checked

new Python passes the strict admitted Mypy profile **and** changed Python does **not**
regress below its passing baseline.

## Test case

add one incompatible return type **and** one unexplained broad suppression **to** a
changed target **in** the admitted Mypy set.

## Acceptance criteria

pass **only** **when** both defects are reported **and** the target is rejected.

## Failure disposition

reject the changed target **until** types agree **or** a narrow explained suppression
is accepted.

## Sources

- [Mypy: strict mode](https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-strict)
- [CA-M-427 — Use Mypy for static Python type checking](../05_method/CA-M-427-PROGRAMMATIC-STANDARD-ENG_POLICY--use-mypy-for-static-python-type-checking.md)
