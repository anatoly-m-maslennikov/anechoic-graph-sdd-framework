---
atom_family: SPEC
atom_id: AN-S-3159
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T19:42:27.572969+00:00"
---

## Summary

Identify local Packages in the Realization Graph

## Claim

### Prose Claim

Give each admitted local folder one Package node across languages. Use its folder postfix to resolve its Package kind.

An unmarked folder with a direct executable is an Implementation Package. Agentic and Asset Packages need no executable. A Test Package can target a Package or a Component.
