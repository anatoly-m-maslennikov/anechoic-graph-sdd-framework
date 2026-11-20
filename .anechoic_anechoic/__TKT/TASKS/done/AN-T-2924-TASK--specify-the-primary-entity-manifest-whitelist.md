---
identity:
  atom_id: AN-T-2924
context:
  container:
    atom: AN-T-2923
  template: task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-20T14:22:40.260187+00:00"
---
## Summary

Specify the primary entity Manifest whitelist

## Work

Define Primary Entity and Property declarations. Limit a Primary Entity
Manifest to identity and Primary/Property classification. An identity
rule can reference Properties that have their own declarations.

Specify State as a Property group owned by Atom. Declare version, status,
and updated_at as Properties of State. Declare Ref ID as derived from
atom_id, State.version, and State.status. Define inheritance and how a
subtype can narrow an inherited Property using its existing declaration.

## References

AN-S-2607, Atom. AN-S-2066, Ref ID.
