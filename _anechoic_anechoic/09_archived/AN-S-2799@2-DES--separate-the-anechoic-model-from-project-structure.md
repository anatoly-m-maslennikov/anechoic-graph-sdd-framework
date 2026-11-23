---
atom_family: SPEC
atom_id: AN-S-2799
container:
  component: C00
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Separate the ANECHOIC model from Project structure

## Claim

ANECHOIC's PROJECT STRUCTURE has:

- Scope Structure.
- Aspects.
- Other declared components.

Its Scope Structure retains the proposed ordered Units:

1. META_MODEL.
2. ENGINE.
3. CORE EXTENSIONS.
4. DOCUMENTATION.

Its Core Meta-Model Unit contains the Atoms defining MODEL//ANECHOIC, including the Declarations for MODEL and PROJECT STRUCTURE. The MODEL and its defining Scope Unit have separate identities.

Each constrained Unit's formal Scope is declared outside that Unit. It states permitted active and passive Subjects, Relations, endpoints and cardinalities.

ANECHOIC's PROJECT STRUCTURE records ENGINE's base formal Scope:

- Implementation RMED uses ENGINE's declared implementation Subjects.
- Instance creation follows that Scope's permissions.
- ENGINE references metamodel Declarations only through passive Subjects.
- Active metamodel definitions use the declared model-defining Scope.
- A local MODEL changes ENGINE's Scope only through an explicit Scope-contract replacement.

Declared Unit order governs this Scope Structure.

## Details

The two root kinds are MODEL and PROJECT STRUCTURE. Their ANECHOIC instance roots are MODEL//ANECHOIC and PROJECT STRUCTURE//ANECHOIC. A consumer Project has its own PROJECT STRUCTURE instance root and may have a local MODEL instance root.

This Draft does not move directories. Exact instance registration and mapping from existing Scope Units remain adoption work. The earlier PROJECT//ANECHOIC Framework wrapper is superseded by the separate typed roots. ANECHOIC's actual Unit names are not universal values.

