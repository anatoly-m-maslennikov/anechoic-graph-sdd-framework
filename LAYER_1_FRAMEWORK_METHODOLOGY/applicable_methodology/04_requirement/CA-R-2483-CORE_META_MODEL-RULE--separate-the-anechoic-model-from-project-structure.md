---
atom_id: CA-R-2483
ref_id: CA-R-2483
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_STRUCTURE
tier: 3
status: active
version: 7
updated_at: '2026-11-13T05:35:40.284468+00:00'
carrier_destination:
  file:
    name: CA-R-2483-CORE_META_MODEL-RULE--separate-the-anechoic-model-from-project-structure.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2483-CORE_META_MODEL-RULE--separate-the-anechoic-model-from-project-structure.md
  source_atom_id: CA-R-2483
  source_atom_revision: 7
  source_sha256: 871767ee68f90622521da106bbe3f9231d15da319269a6e391f5f2323f2a5650
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Separate the ANECHOIC model from Project structure

## Claim

### Prose Claim


`ANECHOIC_MODEL` and `ANECHOIC_STRUCTURE` are distinct namespaces.

- MODEL holds declarations of kinds, Properties and Relations. `Kind//Narrower`
  identifies a narrower kind in MODEL.
- STRUCTURE holds the actual objects. `Whole/Part` follows an immediate
  containment link in STRUCTURE. The canonical Relation is `IS_CONTAINED_BY`,
  from Part to Whole. A Topic names an object by its containment path.

ANECHOIC's PROJECT STRUCTURE has:

- Scope Structure.
- Aspect instances, including Product.
- Other declared components.


Its Scope Structure retains the proposed ordered Units:

1. META_MODEL.
2. ENGINE.
3. CORE EXTENSIONS.
4. DOCUMENTATION.

Its Core Meta-Model Unit contains the Atoms defining `ANECHOIC_MODEL`,
including the Declarations for MODEL and PROJECT STRUCTURE. The MODEL and
its defining Scope Unit have separate identities.

Each constrained Unit's formal Scope is declared outside that Unit. It states permitted active and passive Subjects, Relations, endpoints and cardinalities.

ANECHOIC's PROJECT STRUCTURE records ENGINE's base formal Scope:

- Implementation RMED uses ENGINE's declared implementation Subjects.
- Instance creation follows that Scope's permissions.
- ENGINE references metamodel Declarations only through passive Subjects.
- Active metamodel definitions use the declared model-defining Scope.
- A local MODEL changes ENGINE's Scope only through an explicit Scope-contract replacement.

Declared Unit order governs this Scope Structure.

### Formal Claim

```python
# model
composition(container="Aspects", parts=("Product",))
```

## Details

Each Project has its own STRUCTURE namespace and may define a local MODEL.

