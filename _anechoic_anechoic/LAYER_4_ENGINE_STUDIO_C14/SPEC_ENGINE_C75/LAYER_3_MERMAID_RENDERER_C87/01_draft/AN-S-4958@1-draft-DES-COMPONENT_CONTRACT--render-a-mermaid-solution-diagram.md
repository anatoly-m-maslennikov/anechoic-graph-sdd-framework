---
atom_family: SPEC
atom_id: AN-S-4958
container:
  component: C87
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-4934
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T21:35:58.956802+00:00'
---

## Summary

Render a Mermaid Solution diagram.

## Guarantee

Render a Mermaid diagram for the admitted Solution claim from the normalized formal model. The diagram represents the selected supported claim form.

## Claim

### Formal Claim

```python trace
declare_trace_contract(
    action='render_solution',
    output='rendered',
    must_effect=(('C87.mermaid_diagram', 'rendered'),),
)
```
