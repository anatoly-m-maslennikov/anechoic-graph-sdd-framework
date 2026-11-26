---
atom_family: SPEC
atom_id: AN-S-3034
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:04:42.624158+00:00'
---
## Summary

Identify Atom families and exact revisions independently of carriers

## Claim

### Prose Claim

An Atom is an independently addressable, versioned contribution. Its ID is <project prefix>-<family>-<number>: S for Spec, T for Ticket, and P for Project Meta. An Atom retains its family. Its ID identifies the Atom independently of its carrier, path, filename, lens, or template suffix. A revision reference identifies the exact Atom and Version, including a Draft qualifier when applicable. Filename suffixes may express a template or lens but are not part of the Atom ID.

## Details

Acceptance: AN-S-123-DECISION and AN-S-123-BACK can be filenames for AN-S-123; changing lens, name, or carrier does not change that ID. AN-S-123@1 and AN-S-123@2 designate different exact revisions of the same Atom. A mapped exact legacy reference resolves to its corresponding revision.
Confirmed separate legacy lineages receive distinct Atom IDs and preserve
their versions. An ambiguous legacy revision reference requires its
original source path. Only Draft status uses the Draft qualifier in
Anechoic. An archived withdrawn Draft uses the ordinary Archived reference.
CA-P-3075 owns the frozen inventory, ID map, and
migration batches.

Sources: CA-A-1462@1-draft, CA-R-2508@15. Task: CA-P-3080.
