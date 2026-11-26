---
atom_family: SPEC
atom_id: AN-S-2610
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-25T22:50:38.005067+00:00"
---
## Summary

Classify permission to have parts as Container

## Claim

### Prose Claim


Container is a classification whose admitted value cases are yes and no:


The yes case permits the Node to be the whole endpoint of CONTAINS, subject to its declared endpoint domain and effective Entity constraints. It does not by itself require a part. The no case forbids that endpoint role. Whether a part may belong to a whole is distinct from whether that part may itself have parts.

Use `Node// >| Container = yes` when selecting eligible whole instances. Container is not a required Boolean Property authored on every instance. This Draft does not assign an implicit default or require a classification annotation for every Node.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Node",
    allowed_classification_values={"Container": ("yes", "no")},
)
```

## Details

The Operator chose IS_CONTAINED_BY / CONTAINS and Container: yes/no. Current CA-R-1945@13 distinguishes permission from a requirement to have children; retain that distinction while replacing the old Atom.Enabled Relations.Contains Property representation. Its default-False mechanism is not silently imported into the new general classification. Explicit CONTAINS cardinalities can require parts for a particular Node, such as Workflow.
