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
  status: active
  version: 4
  updated_at: '2026-11-27T12:22:53.034284+00:00'
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

Aggregate a list of comparison status strings. For the input observation,
`has_conflict` means the list contains `conflicting`.
`unresolved_or_empty` means the list is empty or contains `unresolved`.

```python trace
declare_trace_contract(
    action='finding',
    output='reported',
    must_effect=(('C90.source_diagnostic', 'formed'),),
    same_values=(
        (('requested', 'source'), ('result_returned', 'source')),
        (('requested', 'field'), ('result_returned', 'field')),
        (('requested', 'message'), ('result_returned', 'message')),
    ),
)
```

```python trace
declare_trace_contract(
    action='verdict',
    cases={
        'conflicting': {'must_effect': ((
            'C90.verdict_input', 'observed',
            {'has_conflict': True},
        ),)},
        'unresolved': {'must_effect': ((
            'C90.verdict_input', 'observed',
            {'has_conflict': False, 'unresolved_or_empty': True},
        ),)},
        'matched': {'must_effect': ((
            'C90.verdict_input', 'observed',
            {'has_conflict': False, 'unresolved_or_empty': False},
        ),)},
    },
)
```
