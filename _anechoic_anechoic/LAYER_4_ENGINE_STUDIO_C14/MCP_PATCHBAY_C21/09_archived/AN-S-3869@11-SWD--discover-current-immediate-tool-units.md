---
atom_family: SPEC
atom_id: AN-S-3869
container:
  component: C21
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 11
  updated_at: 2026-10-24 06:07:28 +0400
---
## Summary

Discover current immediate Tool units

# Discover current immediate Tool units

## Applicable when

Apply **when** MCP **must** refresh the project-local exposed Tool set.

## Procedure

1. Resolve the current project graph **and** its immediate Tool units owned by `TOOLS`.
2. Match each unit **to** its canonical Tool folder **and** current enablement decision.
3. Exclude nested helpers **and** non-Tool folders from the resulting source set.

## Outcome

MCP has one current, authority-derived source set for Tool exposure.

## Failure or stop

Stop discovery **when** the graph, unit identity, enablement decision, **or** canonical Tool folder is unresolved.
