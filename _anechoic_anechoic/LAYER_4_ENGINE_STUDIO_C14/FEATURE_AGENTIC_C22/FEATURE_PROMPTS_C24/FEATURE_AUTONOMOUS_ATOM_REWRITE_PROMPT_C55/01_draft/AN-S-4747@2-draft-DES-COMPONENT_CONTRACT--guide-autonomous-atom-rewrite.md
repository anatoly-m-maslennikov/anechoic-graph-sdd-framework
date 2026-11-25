---
atom_family: SPEC
atom_id: AN-S-4747
container:
  component: C55
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3062
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T10:52:49+00:00'
---

## Summary

Guide autonomous atom rewrite

## Guarantee

Guide an agent to rewrite selected Atoms while preserving source meaning, and apply an internal gate before a Draft lifecycle call.

## Claim

### Prose Claim

The prompt guides the agent to preserve each selected Atom’s source meaning and forbids reporting unresolved uncertainty as conforming. The carrier does not execute the lifecycle or change Draft or carrier state. This model does not establish agent execution.

### Formal Claim

```python trace
declare_trace_contract(
    action='autonomous_atom_rewrite',
    output='draft_reported',
    must_effect=(('source_meaning_guidance', 'provided'), ('uncertainty_guidance', 'required')),
    forbid_effect=('draft_lifecycle', 'draft_write', 'carrier_state'),
)
```
