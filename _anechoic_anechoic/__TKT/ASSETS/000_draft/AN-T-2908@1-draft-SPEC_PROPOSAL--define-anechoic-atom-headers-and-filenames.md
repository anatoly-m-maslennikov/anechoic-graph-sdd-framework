---
atom_family: TKT
atom_id: AN-T-2908
structure:
  container:
    component: C9
  priority: 2
context:
  template: Spec Proposal
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:11:33.439975+00:00'
---
## Summary

Define Anechoic Atom Headers and filenames

## Proposal

### Header

Use a Markdown carrier with one YAML Header and a single Summary. Store the
stable ID in `identity.atom_id`. Its numeric suffix is a nonempty string of
ASCII digits. Preserve its exact spelling, including leading zeros. Store
status, Version, and update timestamp in `state`. During mechanical
migration, use the captured file modification time in UTC when the
authored timestamp is missing or has no timezone. Record the original
value and captured modification time in the migration receipt.

Derive the family from the ID. Use `context.container` with exactly one
Component ID or Atom ID. Store an authored tier, lens, or template in
Context when applicable. Map the legacy tier `core` to numeric Tier 1.
A PKG Spec stores the Package ID separately from the Atom ID and Summary.

For a migrating legacy carrier with an opening Markdown title and no
Summary, copy the title into a new `## Summary` section. Preserve the
original Markdown bytes below it and record the addition in the receipt.

An explicit `concern` contains `path`, `subject`, and `relation`. Validate
each path hop. A migrated carrier with no mechanically mappable Concern
omits the group and records the original subject in the migration report.
Outgoing relations can use stable IDs or exact revision pins. Derive inverse
endpoints and carrier paths from their authored sources.

### References and filenames

A bare ID selects Current. `ID@Version` selects the exact Current or
Archived revision. `ID@Version-draft` selects the exact Draft. Keep the
stable ID and Version when changing status. A Draft and an Archived
revision with the same Version can coexist as distinct references.

Assign a separate new ID to each approved unnumbered legacy Archive.
Keep its stored Version and map its original path to the new exact
reference. Keep the original digest in the receipt.

Use `ID`, `ID@Version-draft`, or `ID@Version` as the filename marker for
Current, Draft, or Archived. A withdrawn legacy Draft migrates as an
ordinary Archived Atom using `ID@Version`. Keep its old Draft-qualified
reference in the migration map. Follow the filename marker with the optional lens and template
tokens, then `--<summary-slug>.md`. The candidate uses lens then template.
Normalize the Summary slug to lowercase ASCII-alphanumeric runs joined by
hyphens. Preserve the original Summary. Report a Summary with no valid slug.

For example, an Active PKG Spec at version 2 can be
`AN-S-124-SWE-PKG--create-order.md`, addressed exactly as `AN-S-124@2`.
A Draft can be `AN-S-124@3-draft-PKG--create-order.md` when its lens is
omitted. Verify the tree against the family and the basename against the
Header and Summary.

### Carrier directories

- SPEC Drafts and Archives use `draft/` and `archived/` directly under the
  owning Component Spec Section. Active SPEC Atoms use the section’s lens
  directories, for example `DES/`.
- TKT uses `__TKT/TASKS/` and `__TKT/ISSUES/` under the Project records
  directory. Within each branch, Active records live at the branch root.
  Draft and Archived records use that branch’s `draft/` and `archived/`.
  Done, Canceled, and Resolved records use `done/`, `canceled/`, and
  `resolved/` within the corresponding branch. Keep Backlog in that
  branch’s `backlog/` directory. A linked asset goes in its Ticket’s
  directory. Standalone assets use `__TKT/ASSETS/`, with Active at the
  branch root and other admitted statuses in their own subdirectories.
- PMETA Active records live directly in `_PMETA/`. Draft and Archived
  records share `_PMETA/draft/` and `_PMETA/archived/` across record types.

CA-C-746 records the operator’s placement decisions.

CA-P-3087 owns this candidate. CA-P-3075 owns the frozen inventory, ID map,
and migration. Inputs are CA-A-1461, CA-A-1462, CA-A-1463, and CA-A-1465.
