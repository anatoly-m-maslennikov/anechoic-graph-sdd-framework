---
atom_family: SPEC
atom_id: AN-S-2680
concern:
  subject: IS_DERIVED_FROM
  path: Model/Graph/Relation
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_relation
  lens: DOM/CONT
state:
  status: "active"
  version: 42
  updated_at: "2026-11-26T16:34:52.365638+00:00"
---
## Summary

Declare IS_DERIVED_FROM

## Semantics

A derived Artifact records which Carrier content it used. For an Atom projection, the source is the Markdown file identified by its path and the exact Atom revision read from its Header. A Projection can use several sources. Follow the same edge in reverse to find the derived Artifacts for a source.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Carrier, Derived, Relation

class IsDerivedFrom(Relation):
    name = 'IS_DERIVED_FROM'
    relation.inverse_alias = 'IS_SOURCE_FOR'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (Derived,)}
    relation.target_endpoint = {
        'level': 'instances',
        'entity_paths': (Carrier,),
        'reference_form': 'exact_source_content_version',
    }
```
