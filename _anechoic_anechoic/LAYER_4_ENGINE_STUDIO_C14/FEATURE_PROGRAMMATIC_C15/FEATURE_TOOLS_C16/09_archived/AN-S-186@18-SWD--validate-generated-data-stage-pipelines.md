---
atom_family: SPEC
atom_id: AN-S-186
container:
  component: C16
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 18
  updated_at: "2026-11-27T18:09:40.995150+00:00"
---
## Summary

Validate generated data-stage pipelines

# Validate generated data-stage pipelines

## Applicable when

use this Method **when** validating a registered generated-data pipeline from source carriers through derived stages.

## Procedure

1. load the registered `src`, `stg`, `mrt`, **and** `biz` stage declarations, their declared dependencies, **and** their materializations.
2. resolve the authoritative source frontier for **every** declared generated output.
3. check that **every** stage uses one registered prefix, **every** dependency advances from `src` toward `biz`, **and** no generated output becomes semantic authority.
4. compare **every** materialization's recorded input frontier with the current declared source frontier.
5. report **every** unregistered prefix, non-forward dependency, missing source frontier, stale materialization, **and** independently authored derived fact with its exact carrier.

## Outcome

the pipeline has an attributable `src → stg → mrt → biz` topology with current source-derived materializations, **or** explicit blocking violations.

## Failure or stop

block acceptance **when** a stage uses an unregistered prefix, lacks a source frontier, depends non-forward, claims semantic authority, **or** cannot prove currentness.
