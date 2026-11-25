---
atom_family: SPEC
atom_id: AN-S-1229
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 8
  updated_at: 2026-11-02 08:06:47 +0400
---
## Summary

Define Implementation

## Claim

Implementation **means** the actual Code, Prompts, Documentation and Resources that realize RMED for a Project. Directly edited Implementation can be authoritative for what is actually implemented.

## Semantics

Implementation is not a Projection merely because it realizes RMED. Its logical artifacts remain distinct from their Carriers and from the Runtime in which technical execution occurs.

A Projection is a non-authoritative output produced from a declared source selection through a Workflow: source of truth → Workflow → Projection. Changes to a Projection belong in its authoritative sources, followed by a rebuild through its Workflow. A generated view of Implementation is a Projection; that does not make its directly edited sources Projections.

## Details

CA-R-2535 defines Projection and its source-only editing boundary. CA-R-1568 permits a derived view to be delivered as an Implementation output without classifying Implementation as a whole as Projection.
