---
atom_family: SPEC
atom_id: AN-S-4986
container:
  component: C79
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-4494
state:
  status: draft
  version: 1
  updated_at: '2026-11-26T00:00:00Z'
---

## Summary

Describe Godot Project scope

## Guarantee

The Godot Project contains the editable scene and source assets for the Anechoic logo.

## Claim

### Formal Claim

This trace describes the resource boundary; it does not assert a runtime operation or effect.

```python trace
declare_trace_contract(
    action='describe_godot_project_scope',
    output='godot_project_scope_described',
    must_effect=(('godot_project.editable_sources', 'present'),),
)
```
