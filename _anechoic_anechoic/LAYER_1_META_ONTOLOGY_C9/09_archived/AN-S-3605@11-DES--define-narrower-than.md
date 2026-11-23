---
atom_family: SPEC
atom_id: AN-S-3605
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 11
  updated_at: 2026-10-20 04:50:36 +0400
---
## Summary

Define NARROWER_THAN

# Summary

Define NARROWER_THAN

## Scope

the NARROWER_THAN Relation **in** the Terms Graph.

## Claim

a NARROWER_THAN Relation from Term A **to** Term B **in** the Terms Graph **means** that, under their governing definitions, **if** Term A applies **to** a referent, **then** Term B applies **to** the same referent; this Relation does **not** express Property ownership **or** allowed-value membership.

## Semantics

Specialization and bearer dependence are distinct. A dependent kind can itself have narrower kinds. NARROWER_THAN does not establish that either endpoint is primary and does not substitute for IS_BORNE_BY.

## Details

### relation admission

- Status: the NARROWER_THAN Relation Kind is Active.
