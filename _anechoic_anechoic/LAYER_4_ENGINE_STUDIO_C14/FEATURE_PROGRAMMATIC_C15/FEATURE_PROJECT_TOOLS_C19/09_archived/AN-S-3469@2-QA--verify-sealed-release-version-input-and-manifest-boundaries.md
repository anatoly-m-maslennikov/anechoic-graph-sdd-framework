---
atom_family: SPEC
atom_id: AN-S-3469
container:
  component: C19
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-10-11 16:46:21 +0000
---
## Summary

Verify sealed Release Version input and manifest boundaries

# Summary

Verify sealed Release Version input and manifest boundaries

## Scope

Candidate-manifest construction and rejection before any effect.

## Claim

The QA case **must** prove that one local-release command automatically discovers current registered definitions and Action-to-Tool bindings, captures current active-source Atoms at Run start, and produces a deterministic manifest without caller-supplied revision bindings or a separate manifest refresh. It proves that all later candidate phases consume that same snapshot and that changed captured bytes, settings, frontier, destination, digest, duplicate row, traversal, or caller-supplied substitute is rejected without source, runtime, Skill, image, or invented Journal mutation.

## Details

Assert that the manifest includes only the captured active Methodology-source Atoms and all required Engine entries rather than accepting an Engine-Tools-only candidate. A later authoring revision cannot replace a captured row. Preparation may have an empty receipt-reference list before actual Run recording; actual Run receipts belong to the shared Session. This is construction proof, not release success evidence.
