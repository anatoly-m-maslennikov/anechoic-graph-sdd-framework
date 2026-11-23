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
  version: 1
  updated_at: '2026-11-12T09:11:13.653926+00:00'
---
## Summary

Use the current Engine container to build the next image

## Claim

### Prose Claim

Use the current ready Engine container's image to run the Engine steps that build the next image. Give those steps the new build's staged sources. Use the staged sources directly for the first build, when there is no predecessor image.
