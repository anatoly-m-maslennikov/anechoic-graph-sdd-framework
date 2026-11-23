---
atom_family: SPEC
atom_id: AN-S-2318
container:
  component: C27
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 17
  updated_at: '2026-11-23T13:45:43.309920+00:00'
---

## Summary

Bind public release to its own package root

## Scope

the installed-source root of the public-release Tool.

## Claim

### Prose Claim

the public-release Tool **must** retain `LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_3_PUBLIC_RELEASE_C64/` as its own installed package-relative root.

## Details

The rule does not alter `.anechoic_install/releases/<digest>/manifest.toml`, `.anechoic_install/current.toml`, or a Project runtime selection carrier; their owning installation authority remains separate.
