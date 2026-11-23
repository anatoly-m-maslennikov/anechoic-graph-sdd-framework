---
atom_family: SPEC
atom_id: AN-S-1760
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 26
  updated_at: 2026-10-29 07:45:30 +0400
---
## Summary

Serialize External Project Goal References

## Claim scope

references to Current and historical external Project Goal Atoms.

## Claim

**every** Reference **to** a Current external Project Goal Atom **must** use its canonical Current Atom ID, not its current Carrier filename stem.

A Reference **to** an Archived external Project Goal Atom **must** use its canonical Atom ID qualified once with its unchanged numeric Version when historical identity is required. A Current Project Goal reference **must not** omit the canonical ID or fall back to a filename stem; this Delivery creates no ID-less Current exception.

## Details
