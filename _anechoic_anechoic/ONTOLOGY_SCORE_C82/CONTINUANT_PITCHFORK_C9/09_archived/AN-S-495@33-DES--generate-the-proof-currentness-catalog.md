---
atom_family: SPEC
atom_id: AN-S-495
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 33
  updated_at: "2026-11-25T23:20:51.644624+00:00"
---
## Summary

Generate the proof currentness Catalog

## Claim

### Prose Claim


proof-currentness Catalogs generated from governed proof dependency frontiers and their additional invalidation conditions.


ANECHOIC generates a non-authoritative proof-currentness Catalog from governed proof dependency frontiers encoded under GOV REQU 010 **and** their additional invalidation conditions. the Catalog reports **every** proof as `current`, `stale`, **or** `unknown`, marks **only** the smallest direct **and** transitive dependency closure affected by a change, never infers currentness from timestamps alone, **and** never mutates the historical proof record.
