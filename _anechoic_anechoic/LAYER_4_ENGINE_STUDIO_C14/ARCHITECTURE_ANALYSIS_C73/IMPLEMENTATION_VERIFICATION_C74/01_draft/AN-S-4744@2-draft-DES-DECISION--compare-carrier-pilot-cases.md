---
atom_family: SPEC
atom_id: AN-S-4744
container:
  component: C74
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4743@2-draft
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T00:00:00+00:00'
---
## Summary

Compare carrier pilot cases

## Claim

### Prose Claim

Generate the carrier model, collect source and effect evidence, run Lean against the supplied formal blocks, and compare the selected observations. An unavailable Lean executable or failed comparison is unresolved. Findings are limited to the selected cases.

### Formal Claim

```python
component_workflow(
    component='C74',
    action='carrier_compare',
    machine={
        'id': 'c74_compare_carrier_pilot',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'comparison_requested': {'target': 'building', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'carrier_compare', 'detail': {
                        'transport': 'cli', 'runner': 'managed_python',
                        'module': 'ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_compare',
                        'arguments': ['--root <project-root>', '[--lean <executable>]', '[--formal-only]'],
                    }}}},
            }},
            'building': {'on': {
                'model_built_from_python_syntax_and_shape': {'target': 'collecting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'carrier_model', 'outcome': 'built'}}},
                'build_unresolved': {'target': 'unresolved', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'unresolved'}}},
            }},
            'collecting': {'on': {
                'source_and_effect_evidence_retained': {'target': 'comparing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'source_evidence', 'outcome': 'retained'}}},
                'evidence_unresolved': {'target': 'unresolved', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'unresolved'}}},
            }},
            'comparing': {'on': {
                'selected_observations_compared_with_formal_claims': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'selected_cases', 'outcome': 'compared'}}},
                'comparison_or_lean_unresolved': {'target': 'unresolved', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'unresolved'}}},
            }},
            'reporting': {'on': {
                'comparison_reported': {'target': 'compared', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'compared'}}},
            }},
            'compared': {'type': 'final'},
            'unresolved': {'type': 'final'},
        },
    },
)
```
