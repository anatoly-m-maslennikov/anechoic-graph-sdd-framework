---
atom_family: SPEC
atom_id: AN-S-3595
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 7
  updated_at: 2026-10-26 05:59:45 +0400
---
## Summary

Apply authorized Scope Unit cutover losslessly

# Summary

Apply authorized Scope Unit cutover losslessly

## Scope

The mutation boundary for an already assessed and exact-authorized structural proposal.

## Claim

The Tool **must** recheck currentness and apply only the authorized declaration, reference, and explicitly included Carrier changes through one recoverable cutover.

## Details

- Before mutation, the current TOML revision, selected references, authorization, and effective permission must still match the proposal. Any mismatch returns `stale`, `conflict`, or `permission_denied` before mutation.
- Rename and Move repair or explicitly report every affected reference and parent-owned Goal/Atom attachment; Remove never implies recursive Carrier/content deletion and must preserve or explicitly report every affected Atom, definition, and Carrier.
- A failed cutover returns `partial` with applied and unapplied sets plus the authorized recovery boundary. Only that boundary may roll back; the Tool must not overwrite concurrent edits, erase unapproved content, or claim completion.
- Journal evidence follows the existing shared Journal model. Recording failure is returned separately from the structural outcome and does not create a competing schema.
