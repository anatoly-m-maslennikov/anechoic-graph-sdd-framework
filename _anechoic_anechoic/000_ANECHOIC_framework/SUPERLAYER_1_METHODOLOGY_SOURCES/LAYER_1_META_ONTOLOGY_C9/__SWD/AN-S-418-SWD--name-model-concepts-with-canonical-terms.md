---
atom_family: SPEC
atom_id: AN-S-418
structure:
  container:
    component: C9
  tier: 3
context:
  lens: SWD
state:
  status: active
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Name Model Concepts with Canonical Terms

## Claim

### Prose Claim


Authoring names for metamodel and Project concepts.


- Choose names that distinguish their referents.
- Avoid Entity, Type, Content or Value when they add no information.
- Keep useful qualified and compound expressions.
- Use one canonical Term per concept across prose, formal paths and YAML.
- Do not introduce unnecessary synonyms or replace words globally.

## Details

Choose a name from the concept it denotes, not from a neighboring carrier or implementation. For example, prefer `Form` when distinguishing Declaration from other Requirement forms, and `Node` when naming a graph member. Retain `Entity Definition` or `Atom Content` where the established compound expresses the intended concept; do not replace words globally without an approved mapping.
