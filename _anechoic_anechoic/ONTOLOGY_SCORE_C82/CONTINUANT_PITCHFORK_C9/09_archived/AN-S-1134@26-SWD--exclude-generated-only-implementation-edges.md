---
atom_family: SPEC
atom_id: AN-S-1134
container:
  component: C9
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 26
  updated_at: 2026-10-29 07:17:22 +0400
---
## Summary

Exclude generated-only implementation edges

# Summary

Exclude generated-only implementation edges

## Scope

provenance validation of recorded changes in the governed selection.

## Claim

provenance validation inspects **every** recorded change **in** the governed selection. a change contributes an Implementation Relation, implementation coverage, **or** semantic traceability edge **only** **when** it changes **`>=1`** non-generated governed source.

an update **only** **to** generated Projections remains an auditable refresh. it retains its required Journal provenance but cannot become an implementation input **to** the semantic graph that produced the generated Carrier. a mixed change participates **only** through its substantive non-generated governed source changes.

## Details
