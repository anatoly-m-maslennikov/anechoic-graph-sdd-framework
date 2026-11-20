---
atom_family: SPEC
atom_id: AN-S-2414
structure:
  container:
    component: C18
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 32
  updated_at: 2026-11-02 19:46:47 +0400
---
## Summary

Define the BULK_CHANGE Tool unit

## Scope

BULK_CHANGE composition of explicitly approved operations, with independent Actions for Atom targets.

## Claim

### Prose Claim

`BULK_CHANGE` **must** have one Workflow composition owner in TOOL_WORKFLOWS. Its existing executable binding at `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/BULK_CHANGE/` remains unchanged by this authority split and is resolved explicitly from the current execution context; it composes registered create, structured patch, relation change, rename, move, lifecycle, **and** replacement operations over an explicit approved target sequence and emits a complete mutation-free plan. For Atom operations it invokes one independently admitted Action per Atom target, stops at the first failure, retains completed Actions and leaves the remainder untouched; it **must not** promise a cross-Atom rollback or all-or-nothing effect. Preserve each Atom Action's own source, permission, preview and storage-effect safeguards. Resume and retry policy for that sequence is deferred. These Atom rules do not replace separately governed generic Artifact transaction rules.

## Details
