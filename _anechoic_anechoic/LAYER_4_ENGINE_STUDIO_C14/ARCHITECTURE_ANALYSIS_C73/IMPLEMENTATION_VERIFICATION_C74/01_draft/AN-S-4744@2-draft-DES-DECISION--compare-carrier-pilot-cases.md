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

Generate the carrier model, collect source and effect evidence, run Lean against the supplied formal blocks, and compare the selected observations. Report unresolved coverage or execution failure. An unavailable Lean executable or failed comparison is unresolved. Findings are limited to the selected cases. With `--formal-only`, compare authored Contract and Solution cases without building the implementation model or collecting implementation evidence. Manifest comparison and unmodeled behavior remain unresolved.

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
                'build_unresolved': {'target': 'reporting_unresolved', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'coverage', 'outcome': 'unresolved'}}},
            }},
            'collecting': {'on': {
                'source_and_effect_evidence_retained': {'target': 'comparing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'source_evidence', 'outcome': 'retained'}}},
                'evidence_unresolved': {'target': 'reporting_unresolved', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'coverage', 'outcome': 'unresolved'}}},
            }},
            'comparing': {'on': {
                'selected_observations_compared_with_formal_claims': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'selected_cases', 'outcome': 'compared'}}},
                'comparison_or_lean_unresolved': {'target': 'reporting_unresolved', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'coverage', 'outcome': 'unresolved'}}},
            }},
            'reporting': {'on': {
                'comparison_reported': {'target': 'compared', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'compared'}}},
            }},
            'reporting_unresolved': {'on': {
                'unresolved_reported': {'target': 'unresolved', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'unresolved'}}},
            }},
            'compared': {'type': 'final'},
            'unresolved': {'type': 'final'},
        },
    },
)
```

```python
component_workflow(
    component='C74',
    action='carrier_compare_formal_only',
    machine={
        'id': 'c74_compare_formal_carrier_cases',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'formal_only_requested': {'target': 'comparing', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'trigger', 'detail': {'mode': 'formal_only'}}}},
            }},
            'comparing': {'on': {
                'cases_compared': {'target': 'reporting', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'formal_cases', 'outcome': 'compared'}}},
                'coverage_unresolved': {'target': 'reporting_unresolved', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'coverage', 'outcome': 'unresolved'}}},
            }},
            'reporting': {'on': {
                'report_cases': {'target': 'done', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'output', 'outcome': 'formal_compared'}}},
            }},
            'reporting_unresolved': {'on': {
                'report_gap': {'target': 'done', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'output', 'outcome': 'unresolved'}}},
            }},
            'done': {'type': 'final'},
        },
    },
)
```
