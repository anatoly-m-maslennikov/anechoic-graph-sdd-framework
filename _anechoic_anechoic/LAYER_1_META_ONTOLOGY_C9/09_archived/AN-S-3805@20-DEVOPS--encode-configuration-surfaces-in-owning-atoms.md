---
atom_family: SPEC
atom_id: AN-S-3805
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 20
  updated_at: 2026-10-27 19:59:24 +0400
---
## Summary

Encode configuration surfaces **in** owning Atoms

# Summary

Encode configuration surfaces **in** owning Atoms

## Scope

configuration surfaces carried by their owning Atoms.

## Claim

an owning Atom **may** carry an optional machine-readable representation of its own Claim **only** **if** it faithfully preserves that Claim **and** is **not** an independent source. legacy `project_scope_unit_graph` **or** `project_graph_state` YAML maps **may** be read as migration evidence; they **must not** own current Scope Unit declarations, paths, Name/order values, Project identity, Atom prefix, **or** selected Authority Modes. Project initialization inputs belong **to** Project Settings; instance defaults belong **to** Framework Instance Settings; unit declarations **and** explicit unit overrides belong **to** Project Structure. this format does **not** require creation **or** consumption of a structural Projection.

## Details
