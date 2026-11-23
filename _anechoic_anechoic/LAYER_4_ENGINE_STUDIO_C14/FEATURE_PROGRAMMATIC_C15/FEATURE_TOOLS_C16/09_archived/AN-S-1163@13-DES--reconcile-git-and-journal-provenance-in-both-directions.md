---
atom_family: SPEC
atom_id: AN-S-1163
container:
  component: C16
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 13
  updated_at: 2026-10-24 01:28:26 +0400
---
## Summary

Reconcile Git and Journal provenance in both directions

# Reconcile Git and Journal provenance in both directions

the Toolset **must** provide deterministic, idempotent reconciliation **in** both directions between real-change Git commits **and** canonical Journal events. it **must** identify a Git commit **without** its expected Journal event, a Journal event whose bound real-change commit is absent **or** unreachable, duplicate action **or** event bindings, mismatched subject revisions **or** digests, **and** Journal-only commit watermark lag.

reconciliation **may** append missing evidence **only** **when** it can derive that evidence from sealed durable action state **and** reachable repository history **without** invention. **otherwise** it **must** preserve the discrepancy as explicit blocked state for operator resolution. a reconciled action **must** expose its action identity, Initiative, real-change commit SHA, Journal event identity, affected subject identity **and** revision **or** digest, **and** Journal-batch commit SHA.
