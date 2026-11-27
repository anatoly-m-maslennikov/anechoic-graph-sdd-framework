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
  status: active
  version: 4
  updated_at: '2026-11-27T11:36:18.749955+00:00'
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
and retain one normalized Spec Model through translation, validation,
rendering, and comparison. Use one `model_pin` for its selected normalized
claims. Compute it as SHA-256 of UTF-8 JSON with sorted keys, ASCII
escaping, compact separators, and no non-finite numbers. Compare independent
stage observations of the claims actually used; a copied final pin alone
is not evidence of the handoff. A missing or different stage identity
prevents a compared result.

Include each failure field and the source pin when known. When a requested
pin is absent, use the request Manifest as context. Compare the validated
Lean declarations and render the validated Solution projection.
Compare the SHA-256 of the actual rendering input to the validated
Solution's digest. Render the selected Action when one is requested.
For ordinary comparison, bind the C88 input to that Model. For bounded
framing, bind the C86 framing comparison to that Model and report its finite
result. Keep the digest of the validated claims and finite result together
through the return. Do not require C88 on that path.

```python trace
declare_trace_contract(action='verify_pinned_specs', cases={
    'compared': {
        'must_effect': (('C83.pinned_sources', 'loaded'), ('C84.lean_source', 'generated'),
                        ('C86.translation_validation', 'validated'), ('C94.translation', 'accepted'), ('C87.mermaid_diagram', 'rendered'),
                        ('C94.formal_verification', 'compared')),
        'must_precede': ((('C83.pinned_sources', 'loaded'), ('C84.lean_source', 'generated')),
                         (('C84.lean_source', 'generated'), ('C86.translation_validation', 'validated')),
                         (('C86.translation_validation', 'validated'), ('C94.translation', 'accepted')),
                         (('C94.translation', 'accepted'), ('C87.mermaid_diagram', 'rendered'))),
        'same_values': (
            (('C83.pinned_sources', 'source_set'), ('C94.formal_verification', 'source_set')),
            (('C84.lean_source', 'model_pin'), ('C86.translation_validation', 'model_pin')),
            (('C86.translation_validation', 'model_pin'), ('C94.translation', 'model_pin')),
            (('C94.translation', 'solution_pin'), ('C87.mermaid_diagram', 'solution_pin')),
            (('C94.translation', 'model_pin'), ('C94.formal_verification', 'model_pin')),
        ),
        'value_types': {
            ('C83.pinned_sources', 'source_set'): 'nonempty_array',
            ('C94.formal_verification', 'source_set'): 'nonempty_array',
            ('C84.lean_source', 'model_pin'): 'nonempty_string',
            ('C86.translation_validation', 'model_pin'): 'nonempty_string',
            ('C94.translation', 'model_pin'): 'nonempty_string',
            ('C94.translation', 'solution_pin'): 'nonempty_string',
            ('C87.mermaid_diagram', 'solution_pin'): 'nonempty_string',
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
    'generated': {'must_effect': (('C92.framing_cases', 'generated'),)},
    'invalid': {'forbid_effect': ('C92.framing_cases',)},
})
```
