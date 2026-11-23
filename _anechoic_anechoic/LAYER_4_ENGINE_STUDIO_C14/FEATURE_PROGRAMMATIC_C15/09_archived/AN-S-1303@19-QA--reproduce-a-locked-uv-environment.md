---
atom_family: SPEC
atom_id: AN-S-1303
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Reproduce a locked uv environment

# Reproduce a locked uv environment

## Claim checked

one admitted PROGRAMMATIC Python environment **and** governed command are
reproduced from the selected Python boundary, `pyproject.toml`, **and**
`uv.lock` **without** implicit dependency changes.

## Test case

from an empty project environment, run `uv sync --locked` **and** **then** one declared
command through `uv run --locked`.

## Acceptance criteria

pass **only** **when** the locked sync **and** command complete **without** changing
`pyproject.toml` **or** `uv.lock`, the observed interpreter satisfies the
Method-selected Python boundary, **and** the command uses **only** Method-selected
dependencies.

## Failure disposition

reject the reproducibility claim **when** the lock is stale, resolution changes
implicitly, **or** a dependency lacks Method authority.

## Sources

- [CA-M-429 — Use uv as the default Python workflow frontend](../05_method/CA-M-429-PROGRAMMATIC-ENG_POLICY--use-uv-as-the-default-python-workflow-frontend.md)
