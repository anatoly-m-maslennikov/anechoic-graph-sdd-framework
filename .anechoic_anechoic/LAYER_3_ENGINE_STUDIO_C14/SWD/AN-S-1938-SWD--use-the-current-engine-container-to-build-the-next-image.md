---
identity:
  atom_id: AN-S-1938
context:
  container:
    component: C14
  tier: 3
  lens: SWD
state:
  status: active
  version: 3
  updated_at: '2026-11-12T12:32:38.883300+00:00'
---
## Summary

Use the current Engine container to build the next image

## Claim

### Prose Claim

When refreshing declaration-derived build assets, use the current ready Engine container's image to query the new checkout's staged sources through Workbench. Select eligible Current Declarations by Role and declared main Subject, using their Formal Claims as the source. Do not hardcode Declaration Atom IDs. Use the staged sources directly for the first refresh, when no predecessor image has been recorded.

## Semantics

N+1 applies to asset refresh. A build from the existing asset files uses the selected checkout and needs no ANECHOIC runtime or predecessor image.
