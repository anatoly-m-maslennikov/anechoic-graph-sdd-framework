---
atom_family: SPEC
atom_id: AN-S-3598
container:
  component: C16
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 3
  updated_at: 2026-10-23 03:14:50 +0400
---
## Summary

Bind PROJECT_STRUCTURE authority and cutover carriers

# Summary

Bind PROJECT_STRUCTURE authority and cutover carriers

## Scope

Carrier placement and mutation boundaries for the reviewed structural Tool.

## Claim

Delivery **must** bind project structure declarations to the authoritative TOML and treat declared authority/delivery paths and filesystem observations as separate carriers.

## Details

- Only the selected TOML declaration delta and explicitly authorized reference/Carrier repairs are writable at cutover; implementation paths are reported as declared `delivery_path` values, not created or inferred by this Atom.
- The shared Events Journal remains the sole Run evidence source. This Delivery Atom carries references to its receipts, not a duplicate Journal format.
- A partial outcome records actual carrier changes and its authorized recovery boundary; it does not authorize broad deletion or unreported repair.
