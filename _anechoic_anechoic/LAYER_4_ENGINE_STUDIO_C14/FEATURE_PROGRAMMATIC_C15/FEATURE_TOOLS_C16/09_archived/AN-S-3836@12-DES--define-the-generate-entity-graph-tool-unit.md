---
atom_family: SPEC
atom_id: AN-S-3836
container:
  component: C16
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 12
  updated_at: 2026-10-24 02:14:24 +0400
---
## Summary

Define the GENERATE_ENTITY_GRAPH Tool unit

# Define the GENERATE_ENTITY_GRAPH Tool unit

`GENERATE_ENTITY_GRAPH` **must** be an immediate executable projection Doer Tool Scope Unit of `TOOLS`, with authority-relative path `GENERATE_ENTITY_GRAPH` **and** delivery-relative path `GENERATE_ENTITY_GRAPH` under the current configured TOOLS authority **and** delivery roots.

the Tool derives **and** optionally persists a non-authoritative Entity **and** Term graph Projection from one explicitly selected source frontier. it **may** read authority but **must not** create, update, move, archive, promote, upgrade, replace, **or** **otherwise** mutate an Atom, Journal, configuration carrier, **or** other source of truth.
