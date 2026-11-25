---
atom_family: SPEC
atom_id: AN-S-3397
container:
  component: C76
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3396
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T10:55:48.664879+00:00'
---
## Summary

Measure code and Spec and report Package size evidence

## Guarantee

For the admitted Project, report Component code-to-Spec ratios and Package own-size, binding, and dependency evidence. Identify the underlying files, exact Spec bindings, and incomplete classifications. Provide the results through read-only Workbench queries.

## Claim

### Prose Claim

A report identifies its underlying files, exact Spec bindings, and incomplete classifications. It uses captured code inventory and admitted Current Spec measurements. The results are available through read-only Workbench queries.

### Formal Claim

```python trace
declare_trace_contract(
    action='report_code_and_spec_metrics',
    output='report_returned',
    must_effect=(('code_inventory', 'captured'), ('current_spec', 'admitted'), ('file_and_spec_bindings', 'identified')),
)
```

## Details

The trace models a report returned after the listed evidence is available. It does not establish report completeness, validate the inventory or bindings, or check the measurement and ratio calculations. The source does not define a complete-versus-partial report outcome; incomplete classifications must still be identified.
