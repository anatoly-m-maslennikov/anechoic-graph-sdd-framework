---
atom_family: SPEC
atom_id: AN-S-2607
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 7
  updated_at: 2026-11-05 12:58:42 +0400
---
## Summary

Declare Atom

## Claim

### Prose Claim

- Each Atom instance's IS_CONTAINED_BY link targets the Atom or Scope Unit selected by its Header.Container.
- Each Atom instance's HAS_ACTIVE_SUBJECT link targets the declared entity or instance resolved from Header.Topics.Main Subject. An unresolved Subject is a diagnostic.
- Each Atom instance's GOVERNS link targets the canonical Subject governed by its applicable content.
- Relation permissions count outgoing links in the admitted endpoint domain. They do not create links or grant inverse permissions.

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
