---
atom_family: SPEC
atom_id: AN-S-4669
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-10-04 17:12:08 +0000
---
## Summary

Apply an admitted Atom lifecycle change

# Summary

Apply an admitted Atom lifecycle change

## Operation

This Step invokes exactly CA-O-128, apply authorized Atom lifecycle changes, as one Agentic Action. Its context is Integrated under R1527; missing required capability blocks admission, not silent context substitution.

### Input and parameter binding

Bind request kind, complete frozen target/proposal or status/replacement mapping, current models/authority, permissions/effect admission, effect/recovery/Journal capabilities and check expectations from the exact admitted Workflow request and revalidated current evidence. Archive shortcut normalization remains subject to O128's actual status-model guard.

For Update, bind the exact identity-preserving assessment and target/proposal/evidence from the latest completed O145 Step Run in this Workflow whose O067 binding matches the current proposal; do not accept an arbitrary historical pass. For other kinds no Update assessment is fabricated. Bind prior effect/receipt evidence and actual Run/parent references from retained execution state, not guessed success.

Return O128's result and evidence unchanged to the Workflow. This Step has no second Action reference, alternate classifier, routing decision or implicit retry.

## Details

The Workflow decides whether to dispatch or terminate after this result. Every dispatch is a distinct Step Run with its exact O128 definition/input/context binding; completed effects are not replayed when a receipt is pending. Tool adapter calls are implementation details, not extra graph nodes or authority.
