---
atom_family: SPEC
atom_id: AN-S-3013
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "active"
  version: 5
  updated_at: "2026-11-25T20:09:40.645100+00:00"
---
## Summary

Define Component Seed and its Manifest

## Claim

### Prose Claim

A **Component Seed**, also called a **Specified Package** or **Specified PKG**, is a Package with one Component Seed Manifest. It can grow into a Component with a Component Manifest.

Store the Manifest in the owning Component's SPEC Lens. Give it a stable Atom ID. Its required `## Formal Manifest` declares the `CS` ID and applicable boundaries. Purpose, Contract, and Solution are optional sections in that order.

Put the Seed directly under the owning Component Package. Append its ID to its directory name, as in `create_order_CS123`. Keep its implementation, Test Package, and exact Manifest binding there under AN-S-3014.
