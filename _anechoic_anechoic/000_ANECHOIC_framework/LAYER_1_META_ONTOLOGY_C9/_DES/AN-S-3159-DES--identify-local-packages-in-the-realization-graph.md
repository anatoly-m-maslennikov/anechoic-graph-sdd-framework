---
atom_family: SPEC
atom_id: AN-S-3159
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "active"
  version: 4
  updated_at: "2026-11-25T19:42:27.673828+00:00"
---

## Summary

Identify local Packages in the Realization Graph

## Claim

### Prose Claim

Give each admitted local folder one Package node across languages. Use its folder postfix to resolve its Package kind.

Recognize Implementation Packages using the recursive executable rule in AN-S-4837. Exclude Test Package subtrees from that search. Agentic and Asset Packages need no executable. A Test Package can target a Package or a Component.
