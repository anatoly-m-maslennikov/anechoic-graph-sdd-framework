---
identity:
  atom_id: AN-S-25
context:
  container:
    component: C16
  tier: 4
  lens: QA
state:
  status: active
  version: 18
  updated_at: 2026-10-27 19:59:37 +0400
---
# Summary

Plan functional proof that conflicts remain complete, visible, and non-mutating until validly resolved.

## Scope

Functional conflict cases covering retained candidates, deterministic proposals, and no compiler-owned authority change.

## Claim

An implementation **must** prove that every assessed conflict remains visible and blocks publication until its exact permitted disposition is current and reassessed.

## Details

Use fixtures with a duplicate selected Atom identity, unresolved replacement, incompatible retained candidates, unresolved priority, output collision, and one expansion-boundary or incomplete-coverage finding across Core, Extension, and Project Configuration inputs. The report must retain every source participant and one deterministic proposal per finding, set `publishable: false`, and leave source and pre-existing output unchanged. Reordering fixture files, changing an unrelated source, or adding an Extension must not silently select a winner.

For a correction-required conflict, assert that the Tool returns a source-owner proposal and exposes no source-edit operation. For a candidate-selection decision, assert that only the exact current actual Operator decision for the assessed conflict, with independently verified admitted Run and effect evidence and current frontier bindings, can advance it to reselection and reassessment; an optional Journal reference is observational and cannot authorize. Proposal text, priority, LLM output, or a bare configuration record cannot do so. This carrier records planned functional proof, not a runtime pass.

### Sources

- CA-R-1840; CA-R-2118; CA-O-153 v2 through CA-O-156 v2.
