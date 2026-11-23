---
atom_family: SPEC
atom_id: AN-S-2414
container:
  component: C18
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 26
  updated_at: 2026-10-24 12:35:51 +0400
---
## Summary

Define the BULK_CHANGE Tool unit

# Summary

Define the BULK_CHANGE Tool unit

## Scope

BULK_CHANGE composition of explicitly approved operations, with independent Actions for Atom targets.

## Claim

`BULK_CHANGE` **must** have one Workflow composition owner in TOOL_WORKFLOWS. Its existing executable binding at `102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/BULK_CHANGE/` remains unchanged by this authority split and is resolved explicitly from the current execution context; it composes registered create, structured patch, relation change, rename, move, lifecycle, **and** replacement operations over an explicit approved target sequence and emits a complete mutation-free plan. For Atom operations it invokes one independently admitted Action per Atom target, stops at the first failure, retains completed Actions and leaves the remainder untouched; it **must not** promise a cross-Atom rollback or all-or-nothing effect. Preserve each Atom Action's own source, permission, preview and storage-effect safeguards. Resume and retry policy for that sequence is deferred. These Atom rules do not replace separately governed generic Artifact transaction rules.

## Details
