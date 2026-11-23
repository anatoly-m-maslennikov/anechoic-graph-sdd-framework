---
atom_family: SPEC
atom_id: AN-S-2410
container:
  component: C18
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 16
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Accept common Atom target selectors

# Summary

Accept common Atom target selectors

## Scope

Independent logical Find, Read and Modify selection of Atom targets.

## Claim

Atom Find **must** accept composable Scope Unit, Content Role, Type and Subject filters, including direct `governs` and `depends_on` matching under the selected exact, prefix, suffix or contains mode. A connector **may** resolve canonical filenames or locations internally; logical operation targets are Atom identities. Find **must** return matching identities and matching facts without granting effect permission.

Read and Modify **must** accept explicit selected identities independently of Find. Read returns the complete source and exact identity, Version and source pin; Modify binds its explicit target and expected source before its own preview and authorized effect. The Workflow owns supplied selection defaults, source-view and lifecycle criteria and applicable schema and authorization bindings; the connector executes only the explicit resulting request. An explicit logical-ID Read requires no pre-known Version and returns actual exact Version and source-state evidence; an optional pinned or historical expectation must match exactly. Modify requires expected current state and Create requires expected absence. The selector contract supplies no permission or Atom operation semantics. Each Atom Doer owns one target's preflight and effect; a several-target Workflow follows independent Action sequencing. Generic Artifact Tools **may** use selectors **only** as helpers and **must not** become public substitutes for logical Atom operations.

## Details
