---
atom_family: SPEC
atom_id: AN-S-364
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 25
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Journal Projection Rebuild Events

# Summary

Journal Projection Rebuild Events

## Scope

Projection Rebuilds and their Work Journal Actions and terminal Events.

## Claim

**every** Projection Rebuild **must** have **`=1`** Work Journal Action whose terminal Event records the rebuild outcome.

## Details

acceptance of that Event into the Journal does **not**, by itself, make the Projection current. currentness remains subject **to** the Projection's applicable source **and** validation requirements; the accepted Event preserves the observed outcome **without** replacing those requirements.
