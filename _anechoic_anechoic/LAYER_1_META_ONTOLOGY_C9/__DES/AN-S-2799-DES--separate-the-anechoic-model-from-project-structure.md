---
atom_family: SPEC
atom_id: AN-S-2799
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 7
  updated_at: '2026-11-13T05:35:40.284468+00:00'
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

