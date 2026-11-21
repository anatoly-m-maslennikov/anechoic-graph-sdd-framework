---
atom_family: SPEC
atom_id: AN-S-2318
structure:
  container:
    component: C27
  tier: 4
context:
  lens: DevOps
state:
  status: active
  version: 15
  updated_at: 2026-11-11 00:17:19 +0400
---

## Summary

Bind public release to its own package root

## Scope

the installed-source root of the public-release Tool.

## Claim

### Prose Claim

the public-release Tool **must** retain `LAYER_5_FRAMEWORK_DELIVERY/PUBLIC_RELEASE/` as its own installed package-relative root and resolve sibling `RELEASE_VERSION` evidence through the selected installed Framework package.

## Details

The rule does not alter `.anechoic_install/releases/<digest>/manifest.toml`, `.anechoic_install/current.toml`, or a Project runtime selection carrier; their owning installation authority remains separate.
