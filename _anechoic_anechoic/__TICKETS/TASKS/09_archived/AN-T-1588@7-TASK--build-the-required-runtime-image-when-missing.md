---
atom_family: TKT
atom_id: AN-T-1588
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 7
  updated_at: 2026-10-24 13:05:09 +0400
---
## Summary

Build the required runtime image **when** missing

# Summary

Build the required runtime image **when** missing

## Objective

the AI Agent implements the build-if-missing branch for the admitted runtime image.

## Details

- input: the image resolver, accepted build contract, **and** image golden tests.
- output: a bounded build adapter that uses the intended distributive Framework source, resolves the built immutable image ID, **and** preserves an existing working runtime.
- verification: prove one build for an absent required image, no build for a compatible image, **and** truthful build-failure reporting. inspect the build context for excluded Project data, credentials, **and** generated state.
- effort: **`<=15`** minutes for **`=1`** AI Agent; the Epic's decomposition rule applies **before** execution **if** the estimate no longer holds.

### Definition of Done

- completion evidence: all 8 image golden tests passed. the build adapter assembles an exact private source closure, captures **and** re-inspects the immutable digest, checks input freshness **and** preserves existing runtimes. mock-only tests; real Docker build belongs **to** the proof Tasks.

the Plan is **not** Done **if** ((a compatible image is rebuilt unnecessarily) **or** (a failed build produces a ready image result) **or** (build input **or** existing-runtime preservation checks fail)).
