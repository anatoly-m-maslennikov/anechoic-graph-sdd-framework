---
atom_family: SPEC
atom_id: AN-S-2697
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 12
  updated_at: 2026-11-05 16:33:24 +0400
---
## Summary

Define Relation

## Claim

### Prose Claim

Relation defines a reusable directed graph Relation Type with a Name and Meaning. Each actual link is a tuple (Host, Relation Type, Target); an actual edge does not create a separate Relation ID. Endpoints are declared model Entities or instances, including Carrier and Relation descriptors, except that HAS_ALLOWED_VALUE and HAS_VALUE_CONSTRAINT admit literal or constraint-data Targets and their inverse aliases write those data as Hosts. CFEL glyphs are not endpoints. A declared inverse alias model address and its canonical Relation model address are admitted as the Host and Target of IS_INVERSE_ALIAS_FOR. An inverse alias model address is not a separate Relation entity. CFEL syntax does not itself create a graph endpoint.

A canonical Relation Declaration owns shared meaning, endpoint signature and its inverse alias binding when applicable. An inverse alias reverses the written endpoints of the canonical Relation and denotes the same fact; it has no separate Relation Declaration. A qualified derived view retains its source transformation and qualification. A short notation token follows the written name's direction; it does not create a new Relation, a Node or a separate Relation ID.
### Formal Claim

```python
# model
subject_path(address='Relation')
relation(source='Relation.**', name='IS_PROPERTY_OF', target='(Relation, Relation.**)', source_count='1')
relation(source='(Relation, Relation.**)', name='HAS_PROPERTY', target='Relation.**', source_count='0+')
# instances
subject_path(address='$relation[<Relation>]')
relation(source='$relation.**', name='IS_PROPERTY_OF', target='($relation, $relation.**)', source_count='1')
relation(source='($relation, $relation.**)', name='HAS_PROPERTY', target='$relation.**', source_count='0+')
```

