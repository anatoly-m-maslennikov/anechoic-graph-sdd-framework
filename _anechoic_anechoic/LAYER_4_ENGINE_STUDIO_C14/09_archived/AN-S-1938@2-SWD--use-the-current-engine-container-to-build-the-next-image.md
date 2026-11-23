---
atom_family: SPEC
atom_id: AN-S-1938
container:
  component: C14
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 2
  updated_at: '2026-11-12T09:50:45.533304+00:00'
---
## Summary

Use the current Engine container to build the next image

## Claim

### Prose Claim

When refreshing build assets, use the current ready Engine container's image to process the new checkout's staged declarations. Use the staged sources directly for the first refresh, when no predecessor image has been recorded.

## Semantics

N+1 applies to asset refresh. A build from the existing asset files uses the selected checkout and needs no ANECHOIC runtime or predecessor image.
