---
atom_family: SPEC
atom_id: AN-S-2697
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 14
  updated_at: '2026-11-13T06:01:37.766634+00:00'
---
## Summary

Define Relation

## Claim

### Prose Claim

Relation defines a reusable directed graph Relation Type with a Name and Meaning. Each actual link is a tuple (Host, Relation Type, Target); persist each direct fact once. An actual edge does not create a separate Relation ID. Endpoints are declared model Entities or instances, including Carrier and CFEL descriptors, and exclude literal values and glyphs. IS_INVERSE_ALIAS_FOR also admits a declared inverse-alias model address as Host and its canonical Relation model address as Target; the inverse-alias address is not a separate Relation entity. An operator is distinct from a graph Relation even when its notation spells a Relation traversal. Its declared descriptor may be an endpoint.

A direct Relation Declaration owns shared meaning, endpoint signature and any counterpart binding. An inverse alias introduced by its canonical Relation Declaration names the reverse writing of the same fact and is not a separate Relation entity or Declaration. A qualified derived counterpart remains a distinct Relation with its own Declaration; its meaning, endpoint transformation and qualification are retained. An alias supplies lexical notation for one Relation; it does not create a new Relation, a Node or a separate Relation ID.
### Formal Claim

```python
# model
subject_path(address='Relation')
relation(source='Relation.**', name='IS_PROPERTY_OF', target='(Relation, Relation.**)', source_count='1')
relation(source='(Relation, Relation.**)', name='HAS_PROPERTY', target='Relation.**', source_count='0+')
# instances
subject_path(address='Relation//$relation')
relation(source='$relation.**', name='IS_PROPERTY_OF', target='($relation, $relation.**)', source_count='1')
relation(source='($relation, $relation.**)', name='HAS_PROPERTY', target='$relation.**', source_count='0+')
```

