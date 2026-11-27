---
atom_family: SPEC
atom_id: AN-S-4937
container:
  component: C94
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T20:39:08.202192+00:00'
---
## Summary

Declare Diagnostics

## Purpose

Format source-linked gaps and unresolved findings as diagnostics.

## Component Identity

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C90',
        layer=1,
        name='Diagnostics',
        lens_whitelist=['DES', 'SPEC'],
    ),
)
```

## Component Boundaries

```python
{
            'code': {'exports': {
                '_package__shared.finding': {'shared': ['C75', 'C85', 'C86', 'C88', 'C89']},
                '_package__shared.verdict': {'shared': ['C86', 'C88', 'C89']},
            }},
            'io': {'server': {'finding': {'outcomes': {
                'reported': {'must_effect': [('C90.source_diagnostic', 'formed')]},
            }}}},
        }
```

## Component Contract

Form a diagnostic from the source, field, and message of a finding.

```python trace
declare_trace_contract(
    action='finding',
    output='reported',
    must_effect=(('C90.source_diagnostic', 'formed'),),
)
```
