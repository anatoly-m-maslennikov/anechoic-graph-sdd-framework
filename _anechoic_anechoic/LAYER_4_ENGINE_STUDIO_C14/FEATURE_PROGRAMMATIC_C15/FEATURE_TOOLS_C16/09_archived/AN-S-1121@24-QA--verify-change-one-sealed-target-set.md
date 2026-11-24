---
atom_family: SPEC
atom_id: AN-S-1121
container:
  component: C16
tier: 1
context:
  lens: QA
state:
  status: archived
  version: 24
  updated_at: 2026-11-02 19:46:47 +0400
---
## Summary

Verify change one sealed target set

# Verify change one sealed target set

## Claim checked

CA-M-254 applies **only** an explicitly approved unchanged complete `BULK_CHANGE` plan as one validated rollbackable transaction.

## Applicable when

apply whenever registered bulk operations, plan sealing, approval gating, transaction validation, **or** rollback handling changes.

## Test case

inspect the registered `BULK_CHANGE` unit, **then** use one sealed target set **and** registered structured-patch **and** rename effects **to** derive a complete plan. change one target **after** plan approval, **then** restore it **and** apply the unchanged approved plan.

## Acceptance criteria

`BULK_CHANGE` has prefix `BULK_CHANGE`, immediate `TOOLS` owner, `unordered_unit` kind, Structural level `4`, address `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/BULK_CHANGE`, **and** realization path `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/BULK_CHANGE/`. the stale plan changes nothing. the unchanged plan applies **every** declared effect exactly once, exposes one transaction identity **and** final target frontier, **and** leaves no unplanned mutation.

## Failure disposition

reject the realization **and** preserve target set, approved plan, precondition comparison, declared effects, final frontier, transaction identity, **and** rollback evidence.

## Post-effect failure coverage

use an independent fixture **and** the same admitted rollback boundary **to** exercise a failure **after** **`>=1`** planned effect has changed a Carrier **or** reference. inject a later effect failure **or** failed final verification. **if** the complete transaction is published atomically, inject the fault **after** publication **and** **before** successful verification.

- preserve the exact approved plan, sealed before-state, actual fault position, **and** changed-then-restored values.
- verify complete restoration of the planned mutable Carrier **and** reference frontier, **without** modifying unrelated targets **or** erasing accepted Journal history.
- report a failed transaction with its recovery outcome, **not** a successful final frontier. incomplete **or** unverified recovery fails this Evaluation.
- the existing stale-plan rejection case remains required but does **not** establish post-effect rollback.
