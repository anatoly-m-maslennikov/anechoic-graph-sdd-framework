---
atom_family: SPEC
atom_id: AN-S-3433
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

Dispatch one bounded Scope Unit change

# Summary

Dispatch one bounded Scope Unit change

## Scope

The PROGRAMMATIC Tool/PROJECT_STRUCTURE capability for exactly one requested Create, Rename, Move, or Remove Scope Unit change through CA-O-015v8. A filesystem folder is a Carrier observation, not a new Scope Unit declaration.

## Claim

The Tool **must** accept one typed structural request and invoke the accepted CA-O-015 step graph without replacing its authority, Action meaning, transition guards, or shared Run/Journal contract.

## Details

- Input is `operation`, target identity, expected current TOML revision, and an exact proposed declaration delta; Rename/Move additionally name the old and new identity/path/parent, and Remove names the declared preservation or breakage disposition.
- The authoritative tree is `.anechoic_anechoic/project_structure.toml`; the Tool must read declared `authority_path` and `delivery_path` as distinct fields and must not infer either from a folder listing.
- The Tool returns a typed result: `completed`, `no_op`, `blocked`, `stale`, `conflict`, `permission_denied`, `partial`, or `rolled_back`, with exact source identities/revisions, affected identity/reference/Carrier sets, actual effects, and evidence/Run references where they exist.
- `no_op` requires the requested declaration and required reference state already to equal the authorized target; no mutation is performed. A never-started denial has no fabricated Run or journaled completion.
- CA-O-139 through CA-O-144 retain source selection, proposal, assessment, authorization, cutover, and result assessment ownership respectively. Shared Run support remains owned by its existing contract; this Requirement creates no second Journal schema.
