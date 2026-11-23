---
atom_family: SPEC
atom_id: AN-S-1545
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-04 19:29:30 +0000
---
## Summary

Resolve current Atom lifecycle dispatch

# Summary

Resolve current Atom lifecycle dispatch

## Scope

The selected one-Atom lifecycle dispatcher: Create, identity-preserving Update, Replace, and Change Status (including Archive as its shortcut).

## Claim

The dispatcher **must** resolve the operation from the exact current Atom Carrier, requested result, and applicable admitted status model. It must not hardcode a Content Role status vocabulary. It selects Create only for a new Carrier, Update only when identity and Summary remain fixed, Replace when Summary changes, and Change Status for a status-only lifecycle transition; Archive is Change Status with the model-admitted archive status. A missing, ambiguous, stale, or unadmitted model/result stops before mutation and returns that diagnostic.

The dispatcher returns the selected operation, exact target, expected current Version/digest, current model revision, proposed result, and a `replace_handoff` when a Summary change was requested. `replace_handoff` is a required result, not an implicit Update side effect.

## Details

This Requirement reuses the accepted native Create/Update/Archive/Replace requirements and evaluations. It adds no competing status model or Run schema; shared Run evidence is owned by `WORKFLOW_OPERATIONS/RUN_SUPPORT`.
