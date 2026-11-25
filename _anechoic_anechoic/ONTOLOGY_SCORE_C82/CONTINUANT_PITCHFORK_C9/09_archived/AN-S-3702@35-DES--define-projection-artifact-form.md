---
atom_family: SPEC
atom_id: AN-S-3702
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 35
  updated_at: 2026-10-27 16:26:07 +0400
---
## Summary

Define Projection Artifact form

# Summary

Define Projection Artifact form

## Scope

Projections and their authoritative sources.

## Claim

A Projection is a non-authoritative output produced from a declared selection of sources through a Workflow:

source of truth → Workflow → Projection.

A Projection is not edited directly. Changes are made in its authoritative sources, then the Projection is rebuilt through its Workflow. Its sources may include other Projections; represented facts remain traceable through them to the appropriate source of truth under CA-R-1470. Multiple views of the same facts do not create independent authority.

The declared selection identifies the sources actually used. A Projection need not consume every source kind, and its generation need not be byte-deterministic.

## Semantics

Implementation is not a Projection merely because it realizes RMED. Code, tests, prompts, configuration and documentation can be edited directly and can be authoritative for actual implementation. A generated view of Implementation is a Projection when changes belong in its sources and the view is rebuilt.

## Details

The Workflow defines how the selected sources produce the Projection. Carrier materialization remains separate from that derivation under CA-R-1460.
