---
identity:
  atom_id: CA-R-2508
  ref_id: CA-R-2508@14
context:
  container:
    scope_unit: CA-SU-11
  role: Requirement
  form: Declaration
  topics:
    main_subject: ANECHOIC_MODEL <+ Atom
  tier: 3
state:
  status: archived
  version: 14
  updated_at: '2026-11-13T22:57:24.985880+00:00'
destination:
  file:
    name: CA-R-2508@14-CORE_META_MODEL-DECLARATION--declare-atom.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/099_archived
---

## Summary

Declare Atom

## Claim

### Prose Claim

Each Atom instance has exactly one outgoing HAS_ACTIVE_SUBJECT link. Its target is the declared entity or instance resolved from Header.Topics.Main Subject. An unresolved Subject is a diagnostic.

For each Atom instance, the outgoing GOVERNS Relation has cardinality 0..1 and targets only the canonical Subject the Atom governs through its applicable content. These are separate named outgoing permissions and do not grant an inverse or another Relation. The target-omitted bounds count each Atom’s outgoing links within each Relation Declaration’s admissible endpoint domain; they do not create links.

Each Atom instance's outgoing IS_CONTAINED_BY Relation targets the Atom instance or Scope Unit instance selected by its Header.Container.

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
