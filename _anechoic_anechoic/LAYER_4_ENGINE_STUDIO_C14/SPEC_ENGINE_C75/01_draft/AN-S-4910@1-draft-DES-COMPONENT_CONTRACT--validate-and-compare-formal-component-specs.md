---
atom_family: SPEC
atom_id: AN-S-4910
container:
  component: C75
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3395
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T13:37:33Z'
---

## Summary

Validate and compare formal Component Specs.

## Guarantee

Accept exact source pins for a Component Manifest, its Contract, and its
primary Solution. Check each declaration and the links between them.
Return source-linked comparisons in all three directions and generate
Lean and a Mermaid Solution diagram from the same formal model.

`compared` means the comparison ran. Its findings can include conflicts
and unresolved obligations. `incomplete` identifies a missing,
malformed, or unsupported declaration or link that prevents completion.

## Claim

### Formal Claim

```python trace
declare_trace_contract(
    action='verify_formal_chain',
    output='compared',
    must_effect=(('C75.sources', 'validated'),
                 ('C75.lean', 'generated'),
                 ('C75.mermaid', 'generated'),
                 ('C75.manifest_contract', 'compared'),
                 ('C75.manifest_solution', 'compared'),
                 ('C75.contract_solution', 'compared'),
                 ('C75.comparison_complete', 'reported')),
    must_precede=((('C75.sources', 'validated'), ('C75.lean', 'generated')),
                  (('C75.sources', 'validated'), ('C75.mermaid', 'generated')),
                  (('C75.lean', 'generated'), ('C75.comparison_complete', 'reported'))),
)
```

```python trace
declare_trace_contract(
    action='verify_formal_chain',
    output='incomplete',
    must_effect=(('C75.diagnostics', 'reported'),),
    forbid_effect=('C75.comparison_complete',),
)
```
