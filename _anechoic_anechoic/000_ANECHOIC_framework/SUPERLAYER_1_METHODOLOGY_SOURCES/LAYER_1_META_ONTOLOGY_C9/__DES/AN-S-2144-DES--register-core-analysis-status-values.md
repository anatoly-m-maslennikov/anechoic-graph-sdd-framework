---
atom_family: SPEC
atom_id: AN-S-2144
structure:
  container:
    component: C9
  tier: 2
context:
  lens: DES
state:
  status: active
  version: 25
  updated_at: '2026-11-12T21:17:00.590287+00:00'
---
## Summary

Register Core Analysis Status Values

## Claim

### Prose Claim


the default Status value domain of Analysis and Advisory Atoms with Form Analysis Report or Rationale.


the Core Analysis and Advisory Status model **must** inherit the allowed values of Atom.Header.Status and add Done. That Role Status model applies to Analysis and Advisory Atoms with Form Analysis Report or Rationale. An admitted Extension or Project Configuration **may** add values under the applicable complete Role and Form path; it **must not** remove inherited values.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Status",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom.Header.State",
    applies_to_role="Analysis and Advisory",
    applies_to_forms=("Analysis Report", "Rationale"),
    allowed_values=("Done",),
)
```

## Details

this Status belongs to the Analysis and Advisory Atom itself. It does **not** define a Status transition, carrier placement, setting, or a Workflow, Step, or Action Run outcome, receipt, retry state, result, or completion state. CA-R-1727@30 defines the meanings of Draft and Done for Analysis and the meaning of its archival.
