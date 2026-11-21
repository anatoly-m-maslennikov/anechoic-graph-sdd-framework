---
atom_family: SPEC
atom_id: AN-S-21
structure:
  container:
    component: C16
  tier: 4
context:
  lens: QA
state:
  status: active
  version: 14
  updated_at: 2026-10-27 19:59:37 +0400
---
# Summary

Verify complete Terms Graph golden output

## Scope

Functional complete-case proof for the Terms Graph builder.

## Claim

The golden case **must** prove exact governed-Term and admitted-Relation representation, deterministic ancestor/dependency sets, separated namespace, and a truthful `built` result.

## Details

Use a selected readable fixture with governed Definitions, admitted Terms-graph Relations, direct parents/dependencies, and non-cyclic transitive ancestor/dependency closures. Assert all and only selected Terms and internal Relations, defining Claim/Atom path/revision/digest evidence, separate `terms_graph` namespace, stable direct and transitive sets, non-authoritative status, valid complete coverage, and shared receipt references. Generate twice from identical bytes/settings and compare canonical semantic output byte-for-byte; assert no source or Journal mutation. This carrier specifies functional proof, not a runtime pass.

The fixture proves that repeated reusable Term names across qualified Entity paths remain the same governed Term rather than becoming qualified Terms or hierarchy aliases. It admits `NARROWER_THAN` only with source-pinned Relation Kind, direction, endpoint context, and definition implication; it never substitutes `SUBKIND_OF`. Builder-only proof remains source/Journal non-mutating, while any shared executor proof verifies append-only actual Run recording without rewriting earlier Journal evidence.
