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

Validate the emitted Lean declarations against the normalized source
before comparing a trace or shape chain. Validate the executable
structure of each shape.

`compared` means the comparison ran. Its findings can include conflicts
and unresolved obligations. `incomplete` identifies a missing,
malformed, or unsupported declaration or link that prevents completion.

The model binding `request_normalized_model` identifies the normalized
claims for one request. Lean emits those claims. Translation validation
checks the emitted claims against the source, and Mermaid reads the
validated claims for that same request.

## Claim

### Formal Claim

```python trace
declare_trace_contract(
    action='verify_formal_chain',
    output='compared',
    must_effect=(
        ('C83.pinned_sources', 'loaded', {'component': 'C83', 'action': 'load_boundary_model', 'output': 'loaded'}),
        ('C85.formal_declarations', 'normalized', {'component': 'C85', 'action': 'normalize_spec', 'output': 'normalized', 'model': 'request_normalized_model'}),
        ('C84.lean_source', 'generated', {'component': 'C84', 'action': 'compile_lean', 'output': 'compiled', 'model': 'request_normalized_model'}),
        ('C86.lean_declarations', 'validated', {'component': 'C86', 'action': 'validate_translation', 'output': 'matched', 'model': 'request_normalized_model'}),
        ('C87.mermaid_diagram', 'rendered', {'component': 'C87', 'action': 'render_solution', 'output': 'rendered', 'model': 'request_normalized_model'}),
        ('C88.manifest_contract', 'compared', {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared'}),
        ('C88.manifest_solution', 'compared', {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared'}),
        ('C88.contract_solution', 'compared', {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared'}),
        ('C75.comparison_complete', 'reported'),
    ),
    must_precede=(
        (('C83.pinned_sources', 'loaded', {'component': 'C83', 'action': 'load_boundary_model', 'output': 'loaded'}), ('C85.formal_declarations', 'normalized', {'component': 'C85', 'action': 'normalize_spec', 'output': 'normalized', 'model': 'request_normalized_model'})),
        (('C85.formal_declarations', 'normalized', {'component': 'C85', 'action': 'normalize_spec', 'output': 'normalized', 'model': 'request_normalized_model'}), ('C84.lean_source', 'generated', {'component': 'C84', 'action': 'compile_lean', 'output': 'compiled', 'model': 'request_normalized_model'})),
        (('C84.lean_source', 'generated', {'component': 'C84', 'action': 'compile_lean', 'output': 'compiled', 'model': 'request_normalized_model'}), ('C86.lean_declarations', 'validated', {'component': 'C86', 'action': 'validate_translation', 'output': 'matched', 'model': 'request_normalized_model'})),
        (('C86.lean_declarations', 'validated', {'component': 'C86', 'action': 'validate_translation', 'output': 'matched', 'model': 'request_normalized_model'}), ('C87.mermaid_diagram', 'rendered', {'component': 'C87', 'action': 'render_solution', 'output': 'rendered', 'model': 'request_normalized_model'})),
        (('C86.lean_declarations', 'validated', {'component': 'C86', 'action': 'validate_translation', 'output': 'matched', 'model': 'request_normalized_model'}), ('C88.manifest_contract', 'compared', {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared'})),
        (('C86.lean_declarations', 'validated', {'component': 'C86', 'action': 'validate_translation', 'output': 'matched', 'model': 'request_normalized_model'}), ('C88.manifest_solution', 'compared', {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared'})),
        (('C86.lean_declarations', 'validated', {'component': 'C86', 'action': 'validate_translation', 'output': 'matched', 'model': 'request_normalized_model'}), ('C88.contract_solution', 'compared', {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared'})),
        (('C87.mermaid_diagram', 'rendered', {'component': 'C87', 'action': 'render_solution', 'output': 'rendered', 'model': 'request_normalized_model'}), ('C88.manifest_contract', 'compared', {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared'})),
        (('C87.mermaid_diagram', 'rendered', {'component': 'C87', 'action': 'render_solution', 'output': 'rendered', 'model': 'request_normalized_model'}), ('C88.manifest_solution', 'compared', {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared'})),
        (('C87.mermaid_diagram', 'rendered', {'component': 'C87', 'action': 'render_solution', 'output': 'rendered', 'model': 'request_normalized_model'}), ('C88.contract_solution', 'compared', {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared'})),
        (('C88.manifest_contract', 'compared', {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared'}), ('C75.comparison_complete', 'reported')),
        (('C88.manifest_solution', 'compared', {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared'}), ('C75.comparison_complete', 'reported')),
        (('C88.contract_solution', 'compared', {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared'}), ('C75.comparison_complete', 'reported')),
    ),
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
