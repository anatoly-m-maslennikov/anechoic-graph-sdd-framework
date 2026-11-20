---
identity:
  atom_id: AN-S-3030
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:02:54.132508+00:00'
---
## Summary

Define the Project and Component structure

## Claim

### Prose Claim

A Project has a root Project Component. A Component has a Component Spec Section and a Component Package in REAL and may contain child Components. Component code may contain ordinary Packages. A Module is one source file; a Unit is a function, class, or method. `child_of` points to the parent Component and its inverse supplies children. Layers order siblings where needed. Within an ordered sibling group, imports may target only upstream siblings with lower layer numbers. Downstream imports are forbidden. Unordered siblings have no layer restriction. Each Atom tier is local to its containing Component.

## Details

Acceptance: Anechoic has exactly three direct children: Meta-ontology, Meta-methodology, and Engine Studio. Kernel Mixer, Backend Deck, IWE Console, and MCP Patchbay are children of Engine Studio, not direct children of Anechoic.

Sources: CA-A-1461@1-draft, CA-A-1463@1-draft. Task: CA-P-3079.
