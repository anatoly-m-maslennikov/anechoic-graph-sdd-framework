---
atom_family: SPEC
atom_id: AN-S-2318
container:
  component: C27
tier: 4
context:
  lens: DevOps
state:
  status: "archived"
  version: 16
  updated_at: '2026-11-21T21:49:04.407565+00:00'
---

## Summary

Bind public release to its own package root

## Scope

the installed-source root of the public-release Tool.

## Claim

### Prose Claim

the public-release Tool **must** retain `LAYER_5_FRAMEWORK_DELIVERY/PUBLIC_RELEASE/` as its own installed package-relative root.

## Details

The rule does not alter `.anechoic_install/releases/<digest>/manifest.toml`, `.anechoic_install/current.toml`, or a Project runtime selection carrier; their owning installation authority remains separate.
