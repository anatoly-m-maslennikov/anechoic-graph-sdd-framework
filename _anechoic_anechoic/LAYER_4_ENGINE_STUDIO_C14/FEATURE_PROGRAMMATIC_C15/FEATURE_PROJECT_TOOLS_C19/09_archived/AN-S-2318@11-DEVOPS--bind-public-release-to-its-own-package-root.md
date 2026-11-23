---
atom_family: SPEC
atom_id: AN-S-2318
container:
  component: C19
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 11
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Bind public release to its own package root

# Summary

Bind public release to its own package root

## Scope

the installed-source root of the public-release Tool.

## Claim

the public-release Tool **must** retain `PROJECT_TOOLS/PUBLIC_RELEASE/` as its own installed package-relative root and resolve sibling `RELEASE_VERSION` evidence through the selected installed Framework package.

## Details

The rule does not alter `.anechoic_install/releases/<digest>/manifest.toml`, `.anechoic_install/current.toml`, or a Project runtime selection carrier; their owning installation authority remains separate.
