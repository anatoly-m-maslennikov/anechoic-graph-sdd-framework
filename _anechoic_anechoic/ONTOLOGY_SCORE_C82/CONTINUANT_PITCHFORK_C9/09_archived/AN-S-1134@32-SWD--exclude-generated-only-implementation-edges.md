---
atom_family: SPEC
atom_id: AN-S-1134
container:
  component: C9
tier: 3
context:
  lens: SWD
state:
  status: "archived"
  version: 32
  updated_at: "2026-11-25T22:52:59.161832+00:00"
---
## Summary

Exclude generated-only implementation edges

## Claim

### Prose Claim


provenance validation of recorded changes in the governed selection.


provenance validation inspects **every** recorded change **in** the governed selection. a change contributes an Implementation Relation, implementation coverage, **or** semantic traceability edge **only** **when** it changes **`>=1`** non-generated governed source.

an update **only** **to** generated Projections remains an auditable refresh. it retains its required Journal provenance but cannot become an implementation input **to** the semantic graph that produced the generated Carrier. a mixed change participates **only** through its substantive non-generated governed source changes.
