---
atom_id: CA-R-2247
ref_id: CA-R-2247
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Relation
tier: 1
status: active
version: 16
updated_at: '2026-11-13T22:35:15.466785+00:00'
carrier_destination:
  file:
    name: CA-R-2247-CORE_META_MODEL-DECLARATION--define-relation.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2247-CORE_META_MODEL-DECLARATION--define-relation.md
  source_atom_id: CA-R-2247
  source_atom_revision: 16
  source_sha256: 4ef95537d658cd1fd9cbf1012cd033797e750264acae9b45d9aa12dd9dd40961
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Define Relation

## Claim

### Prose Claim

A Relation applies to Model entities and instances by default. An explicit endpoint level restricts the Host or Target independently. Use explicit endpoint levels when a Relation applies only at one level or connects an instance to its Model entity.

Relation defines a reusable directed graph Relation Type with a Name and Meaning. Each actual link is a tuple (Host, Relation Type, Target); persist each direct fact once. An actual edge does not create a separate Relation ID. Endpoints are declared model Entities or instances, including Carrier and CFEL descriptors, and exclude literal values and glyphs. IS_INVERSE_ALIAS_FOR also admits a declared inverse-alias model address as Host and its canonical Relation model address as Target; the inverse-alias address is not a separate Relation entity. An operator is distinct from a graph Relation even when its notation spells a Relation traversal. Its declared descriptor may be an endpoint.

A direct Relation Declaration owns shared meaning, endpoint signature and any counterpart binding. An inverse alias introduced by its canonical Relation Declaration names the reverse writing of the same fact and is not a separate Relation entity or Declaration. A qualified derived counterpart remains a distinct Relation with its own Declaration; its meaning, endpoint transformation and qualification are retained. An alias supplies lexical notation for one Relation; it does not create a new Relation, a Node or a separate Relation ID.
Each Relation Property has exactly one bearer, which is the Relation or another Relation Property. Each Relation or Relation Property may bear zero or more Relation Properties. The same rules apply to instances and their Properties.

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity

class Relation:
    pass

declare_entity(entity_name='Relation', entity_class=Relation)
```

