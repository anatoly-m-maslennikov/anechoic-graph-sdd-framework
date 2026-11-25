---
atom_family: SPEC
atom_id: AN-S-4880
container:
  component: C37
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3078
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T00:00:00+00:00'
---

## Summary

Derive an Entity and Term Projection.

## Guarantee

This Contract covers read-only Entity and Term projection derivation. Reject an absent, ambiguous, escaping or unreadable source frontier before construction. Return a diagnostic for rejection, without a Projection or writes.

For one selected frontier, return a reproducible, non-authoritative Projection and source Carrier path and digest lineage. Bind selection, authority, profile and settings as specified by AN-S-2524@19. Unknown or unparseable regions remain visible with diagnostics; they do not prove absence. Unsupported required coverage prevents a built or no-op disposition.

Retain the declared Terms, parents and dependency closure subject to source recognition and admission under AN-S-2524@19. Report cycles and actual cardinality violations as Projection data with a failed validation disposition. Identical readable source bytes and settings produce byte-identical semantic output in stable order, subject to the bound authority and profile.

This Contract models no persistence and no Project Scope Unit graph. The Active source Specs govern their broader scope. Current Atoms, Journals, Settings Artifacts and other admitted authority remain authoritative independently of this result.

## Claim

### Formal Claim

```python trace
declare_trace_contract(
    action='derive_entity_projection', output='projection_returned',
    must_effect=(('selected_frontier', 'captured'), ('projection_result', 'returned'), ('source_lineage', 'returned')),
    must_precede=((('selected_frontier', 'captured'), ('projection_result', 'returned')),),
    forbid_effect=('authority_write', 'projection_write'),
)
```

```python trace
declare_trace_contract(
    action='derive_entity_projection', output='frontier_rejected',
    must_effect=(('frontier_error', 'returned'),),
    forbid_effect=('projection_result', 'authority_write', 'projection_write'),
)
```
