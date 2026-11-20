---
identity:
  atom_id: AN-S-2607
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 15
  updated_at: '2026-11-14T07:30:42.506236+00:00'
---
## Summary

Declare Atom

## Claim

### Prose Claim

Each Atom instance has exactly one outgoing HAS_ACTIVE_SUBJECT link. Its target is the declared entity or instance resolved from Header.Topics.Main Subject. An unresolved Subject is a diagnostic.

For each Atom instance, the outgoing GOVERNS Relation has cardinality 0..1 and targets only the canonical Subject the Atom governs through its applicable content. Apply the bounds to outgoing links in the endpoint domain of each Relation Declaration.

Each Atom instance's outgoing IS_CONTAINED_BY Relation targets the Atom instance or Scope Unit instance selected by its Header.Container.

A specializing Atom Claim makes the target Claim more specific or stricter within the same or a narrower Scope and preserves its applicable constraints. A reference or dependency alone does not establish SPECIALIZES.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Continuant

class Atom(Continuant):
    pass

declare_entity(
    entity_name="Atom",
    entity_class=Atom,
    dependent_property_cardinality=2,
    dependent_property_name_format=str,
    allowed_dependent_property_names=("Header", "Content"),
    population_unique_constraints=(
        {"keys": ("Header.Identity.ID", "Header.State.Version")},
    ),
    instance_relation_constraints={
        "IS_CONTAINED_BY": {"targets_per_source": 1},
        "HAS_ACTIVE_SUBJECT": {"targets_per_source": 1},
        "GOVERNS": {"targets_per_source": Cardinality(minimum=0, maximum=1)},
        "CONTRIBUTES_TO": {"targets_per_source": Cardinality(minimum=0, maximum=None)},
        "IS_REPLACEMENT_FOR": {"targets_per_source": Cardinality(minimum=0, maximum=None)},
    },
)
```

## Semantics

An Atom is the smallest independently governed Object.
