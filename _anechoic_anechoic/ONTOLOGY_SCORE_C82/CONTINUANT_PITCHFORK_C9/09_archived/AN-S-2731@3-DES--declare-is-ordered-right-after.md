---
atom_family: SPEC
atom_id: AN-S-2731
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: '2026-11-13T19:17:38Z'
---

## Summary

Declare IS_ORDERED_RIGHT_AFTER

## Claim

### Prose Claim

IS_ORDERED_RIGHT_AFTER applies only to sibling Property instances within Atom.Header or Atom.Content. Both endpoints must share the same immediate bearer. The Host immediately follows the Target in that bearer's sibling order. Ordering is acyclic. Each Property instance has at most one immediate predecessor and one immediate successor. The inverse alias IS_ORDERED_RIGHT_BEFORE reads the same link in reverse.

`x ;> y` means x is immediately before y, in the order x; y. `x <; y` means x is immediately after y, in the order y; x.

Derive one canonical chain for each ordered sibling group from the predecessor pairs in its applicable Property Declarations. For each bearer instance, skip absent Properties and retain the order of the Properties that are present. Each adjacent pair in that chain supplies one `IS_ORDERED_RIGHT_AFTER` link. For example, if the declared order is Form, Label, Topics and Label is absent, Topics immediately follows Form.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_relation

declare_relation(
    relation_name='IS_ORDERED_RIGHT_AFTER',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom.Header.**', 'Atom.Content.**')},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom.Header.**', 'Atom.Content.**')},
    inverse_alias='IS_ORDERED_RIGHT_BEFORE',
    written_alias='<;',
    reverse_written_alias=';>',
    targets_per_source=Cardinality(minimum=0, maximum=1),
    sources_per_target=Cardinality(minimum=0, maximum=1),
    same_immediate_bearer=True,
    acyclic=True,
)
```

## Semantics

IS_ORDERED_RIGHT_AFTER relates a Property instance to its immediately preceding sibling.

