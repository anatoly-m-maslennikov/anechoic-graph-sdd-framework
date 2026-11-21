---
atom_family: SPEC
atom_id: AN-S-2785
container:
  component: C45
tier: 7
context:
  lens: QA
state:
  status: draft
  version: 5
  updated_at: '2026-11-13T22:33:00.097252+00:00'
---
## Summary

Verify canonical direct and inverse relation facts

## Claim

### Prose Claim

#### Registry and facts

Verify Current Requirement relation Declarations, including Relation Declaration, register admitted direct facts and inverse aliases; Draft Declarations do not change the Current registry. Either authored direction materializes one canonical direct fact, swaps inverse endpoints once, and does not duplicate direct or inverse views. Exact model addresses are required; unique case-folding applies only to carrier keys.

Verify container facts use effective Header.Container and the Project root resolves to `uppercase(Project prefix)-SU-00`. Ambiguous names, inverse metadata or case-colliding native labels warn and omit affected facts and bindings without choosing a winner. Unrelated facts and source bytes stay unchanged. Prose, general CFEL and qualified derivations are never runtime facts.

#### Refresh and parity

Verify create, edit, move, rename, delete, invalidate and repair refresh affected direct and inverse facts and hashes. Missing targets remain references; reappearance does not duplicate them. Compare single-source and multi-source final columns, traversal and hashes with a full rebuild. Unrelated edits remain incremental.
