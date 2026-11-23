---
atom_family: TKT
atom_id: AN-T-1587
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

Implement compatible image selection

# Summary

Implement compatible image selection

## Objective

the AI Agent implements the accepted image-compatibility check for the requested Framework runtime.

## Details

- input: the image RMED, image golden tests, **and** `102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/203_APPS/WORKFLOW_ORCHESTRATOR/docker/image_reference.py`.
- output: one resolver that distinguishes image absence from an incompatible existing image, checks the accepted runtime/source identity, **and** returns an immutable admitted image ID.
- verification: prove compatible reuse, stale-source handling, unknown identity, **and** explicit image selection; a familiar mutable tag alone is insufficient evidence.
- effort: **`<=15`** minutes for **`=1`** AI Agent; the Epic's decomposition rule applies **before** execution **if** the estimate no longer holds.

### Definition of Done

- completion evidence: strict immutable-image resolution **and** source fingerprinting are implemented; the resolver-only golden tests passed with exact OS/architecture admission. Build behavior remains the next Task.

the Plan is **not** Done **if** ((tag existence alone admits an image) **or** (the selected image identity is mutable **or** ambiguous) **or** (the image-admission tests fail)).
