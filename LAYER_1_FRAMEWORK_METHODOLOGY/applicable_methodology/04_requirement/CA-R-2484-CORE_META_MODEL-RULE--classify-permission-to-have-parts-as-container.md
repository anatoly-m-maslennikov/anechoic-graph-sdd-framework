---
atom_id: CA-R-2484
ref_id: CA-R-2484
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Node >| Container
tier: 3
status: active
version: 4
updated_at: '2026-11-14T07:32:15.679073+00:00'
carrier_destination:
  file:
    name: CA-R-2484-CORE_META_MODEL-RULE--classify-permission-to-have-parts-as-container.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2484-CORE_META_MODEL-RULE--classify-permission-to-have-parts-as-container.md
  source_atom_id: CA-R-2484
  source_atom_revision: 4
  source_sha256: 62ef7ec978a8fe27062c4de48c2138826471ca340745d87d4f5c6eb1dc31c7ac
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
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
