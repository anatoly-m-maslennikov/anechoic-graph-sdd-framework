---
atom_family: SPEC
atom_id: AN-S-3013
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 4
  updated_at: "2026-11-23T01:48:06.188403+00:00"
---
## Summary

Define Component Seed and its Manifest

## Claim

### Prose Claim

A **Component Seed**, also called a **Specified Package** or **Specified PKG**, is a Package with one Component Seed Manifest. It can grow into a Component with a Component Manifest.

Store the Manifest in the owning Component's SPEC Lens. Give it a stable Atom ID and these sections in order.

1. `## Formal Manifest` declares its `CS` ID and boundaries.
2. `## Purpose` states why it exists.
3. `## Solution` states how it fulfills its Purpose.

Put the Seed directly under the owning Component Package. Append its ID to its directory name, as in `create_order_CS123`. Keep its implementation, Test Package, and exact Manifest binding there under AN-S-3014.
