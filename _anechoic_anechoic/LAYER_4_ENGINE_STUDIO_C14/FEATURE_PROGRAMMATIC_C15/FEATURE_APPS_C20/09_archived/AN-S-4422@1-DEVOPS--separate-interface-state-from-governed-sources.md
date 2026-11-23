---
atom_family: SPEC
atom_id: AN-S-4422
container:
  component: C20
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-11-10 12:28:12 +0400
---
## Summary
Separate interface state from governed sources

## Claim

### Prose Claim

GRAPH_UI interface-state Carriers **must** remain separate from governed source Artifacts **and** from the delivered frontend assets.

- filter **and** focused-node state use their existing URL representation under CA-M-153; transient interface state remains session-local **unless** an explicit retained-state binding applies.
- retained UI service state uses its declared project-local runtime location. disposable frontend build output **and** caches use Project Temporary State under CA-D-437.
- retained state identifies its interface owner **and** referenced source frontier; it **must not** carry an independently authoritative copy of an Atom, Journal, **or** graph Projection.

The frontend Delivery declaration retains ownership of frontend placement. this state boundary does **not** split embedded assets, select a new browser-output filename, **or** change the declared App service contract.
