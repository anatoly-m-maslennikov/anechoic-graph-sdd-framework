---
atom_family: SPEC
atom_id: AN-S-1317
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 21
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Verify one Python technical configuration boundary

# Verify one Python technical configuration boundary

## Claim checked

the selected Python series **and** development-tool profiles have one canonical
technical materialization distinct from ANECHOIC project settings.

## Test case

compare the root `pyproject.toml`, local workflow, **and** automated workflow
selections for the interpreter **and** one admitted development tool.

## Acceptance criteria

pass **only** **when** **all** consumers resolve the current interpreter boundary
selected by CA-M-412 **and** the same admitted development-tool profile,
**and** no ANECHOIC runtime setting is duplicated **in** `pyproject.toml`.

## Failure disposition

reject the conflicting carrier **or** workflow **until** one Method-owned selection is
materialized once.

## Sources

- [PyPA: `pyproject.toml` specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
- [CA-M-412 — Declare one Python and software configuration boundary](../05_method/CA-M-412-PROGRAMMATIC-ENG_POLICY--declare-one-python-and-software-configuration-boundary.md)
