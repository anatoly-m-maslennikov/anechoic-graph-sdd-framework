---
atom_family: SPEC
atom_id: AN-S-1265
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 23
  updated_at: 2026-10-27 19:59:31 +0400
---
## Summary

Verify deterministic transformation from declared inputs

# Verify deterministic transformation from declared inputs

## Claim checked

one declared deterministic PROGRAMMATIC transformation produces its result **and**
failure values from explicit declared inputs **without** an implicit host
observation **or** external effect.

## Applicable conditions

apply **when** a component parses, classifies, validates, plans, projects,
formats, **or** **otherwise** transforms explicit input into a result.

## Test case

evaluate one transformation twice with the same declared input while varying
an **otherwise** irrelevant host observation.

## Acceptance criteria

pass **only** **when** both results **and** failure values are equivalent **and** the
transformation reports no filesystem, process, clock, environment, network,
persistence, **or** logging-export effect.

## Failure disposition

stop treating the unit as deterministic **and** assign its missing observation **or**
effect boundary **to** the appropriate owner.

## Sources

- [CA-M-407 — Allocate deterministic transformations to functions](../05_method/CA-M-407-PROGRAMMATIC-ENG_POLICY--allocate-deterministic-transformations-to-functions.md)
