---
atom_family: SPEC
atom_id: AN-S-5020
container:
  component: C75
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: archived
  version: 3
  updated_at: '2026-11-26T23:28:14.968347+00:00'
---
## Summary

Declare Formal Specification

## Purpose

Verify Component Boundaries, embedded Contracts, and Solutions from exact source pins in a Project Spec snapshot.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C94',
    name='FORMAL_SPECIFICATION',
    layer=2,
    lens_whitelist=['DES', 'SPEC'],
)
```

## Component Boundaries

```python
{'code': {'imports': ['C95'], 'exports': {}},
 'state': {'reads': ['pinned Component Spec rows'], 'writes': []}}
```

## Component Contract

### Verify a pinned formal chain

Use one selected snapshot for all requested pins. Report the exact sources
and retain one normalized Model through validation, rendering, and the
comparison report. Include each failure field and the source pin when
known. When a requested pin is absent, use the request Manifest as context. Compare the validated
Lean declarations and render the Solution from those declarations.
Use the bounded framing comparison already returned by validation when
the selected pair is a bounded framing pair.

```python trace
declare_trace_contract(action='verify_pinned_specs', cases={
    'compared': {
        'must_effect': (('C83.pinned_sources', 'loaded'), ('C84.lean_source', 'generated'),
                        ('C94.translation', 'accepted'), ('C87.mermaid_diagram', 'rendered'),
                        ('C94.formal_verification', 'compared')),
        'must_precede': ((('C83.pinned_sources', 'loaded'), ('C84.lean_source', 'generated')),
                         (('C84.lean_source', 'generated'), ('C94.translation', 'accepted')),
                         (('C94.translation', 'accepted'), ('C87.mermaid_diagram', 'rendered'))),
        'same_values': (
            (('C83.pinned_sources', 'source_set'), ('C94.formal_verification', 'source_set')),
            (('C84.lean_source', 'model_pin'), ('C94.translation', 'model_pin')),
            (('C94.translation', 'model_pin'), ('C87.mermaid_diagram', 'model_pin')),
            (('C87.mermaid_diagram', 'model_pin'), ('C94.formal_verification', 'model_pin')),
        ),
        'value_types': {
            ('C83.pinned_sources', 'source_set'): 'nonempty_array',
            ('C94.formal_verification', 'source_set'): 'nonempty_array',
            ('C84.lean_source', 'model_pin'): 'nonempty_string',
            ('C94.translation', 'model_pin'): 'nonempty_string',
            ('C87.mermaid_diagram', 'model_pin'): 'nonempty_string',
            ('C94.formal_verification', 'model_pin'): 'nonempty_string',
        },
    },
    'incomplete': {
        'must_effect': (('C94.source_diagnostic', 'reported'),),
        'value_types': {('C94.source_diagnostic', 'field'): 'nonempty_string',
                        ('C94.source_diagnostic', 'source'): 'object'},
        'forbid_effect': ('C94.formal_verification',),
    },
})
```

### Generate cases from a pinned formal chain

Generate bounded Python framing cases through Test Generation. Preserve
the source pins. Raise an explicit error when the chain is invalid.

```python trace
declare_trace_contract(action='generate_pinned_cases', cases={
    'generated': {'must_effect': (('C94.generated_cases', 'ready'),)},
    'invalid': {'forbid_effect': ('C94.generated_cases',)},
})
```
