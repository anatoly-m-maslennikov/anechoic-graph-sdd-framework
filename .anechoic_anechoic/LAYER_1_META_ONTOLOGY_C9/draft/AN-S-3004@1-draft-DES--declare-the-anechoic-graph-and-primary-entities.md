---
identity:
  atom_id: AN-S-3004
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:04:29.828572+00:00'
---
## Summary

Declare the Anechoic graph and primary entities

## Claim

### Prose Claim

A Model has a Graph, an eDSL, and Carriers. A Graph consists of Nodes and Relations. Artifact and Ephemeral narrow Node. Atom, Event Record, Component, and Package narrow Artifact. Spec Atom, Ticket Atom, and PMETA Atom narrow Atom. Project narrows Component; Component Package narrows Package. A Component has a Component Spec Section and a Component Package. A Package may contain Packages and Modules; a Module may contain Units. The eDSL is Python for writing Manifests; Format and Cardinality belong to the eDSL.

A View presents information derived from source Atoms and Relations. A View is the new name for the Current Projection; Workspace and its editable SQL View belong to the Workbench model.

## Details

Acceptance: a Project is a Component and an Artifact; a Component Package is a Package; an Ephemeral Node is not thereby an Artifact. A derived View does not become the authored source of its facts.

Sources: CA-A-1462@1-draft. Task: CA-P-3080.
