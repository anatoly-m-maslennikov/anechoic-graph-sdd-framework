---
atom_family: SPEC
atom_id: AN-S-3160
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 7
  updated_at: '2026-11-21T15:48:18+00:00'
---

## Summary

Define the native Atom Carrier format

## Claim

The Atom Carrier is the source of truth. The YAML Header carries the
Atom's Properties. The Markdown Content follows the Header.

### Header order

1. `atom_family` is required. Use SPEC, TKT, or PMETA.
2. `atom_id` is required. Its project prefix and numeric identity remain
   stable. Its family marker is S, T, or P and agrees with Atom Family.
3. `concern` is optional on Atom. An explicit Concern names its subject,
   path, and relation, in that order.
4. `structure` contains the required Container, then Tier when a SPEC Atom
   declares it. A Container references one Component or Atom.
5. `context` carries Template, optional TKT Label, then SPEC Lens.
   TKT and Current PMETA require Template. A PMETA Draft can omit it.
   SPEC can declare Template according to its Template rule.
6. `relations` is optional on Atom. Each entry follows the target reference
   form and endpoint rules of its declared Relation.
7. `state` carries Status, Version, and Updated At, in that order.

TKT stores integer Priority in Structure after Container. Set the Priority
of every migrated Ticket to 2. Use 2 as the default for new Tickets.
Preserve previous authored values in the migration evidence.

### Ticket containment

A planning Ticket uses the Task Template and can contain planning Tickets
and Assets at every depth. Place new bound Assets in `ASSETS/` in the
owning Ticket's companion folder. TKT Assets holds unbound Assets.

The Label is for navigation in Workbench and derived filenames. AN-S-3176
declares its vocabulary. Default to `Subtask` for a Task under a Task and
`Sub-epic` for an Epic under an Epic. An explicit Label takes precedence.

Changing a planning Ticket preserves its containment tree at every depth.
Move its companion folder with the Ticket when its path changes.

Promote its contained planning Tickets recursively when it moves from
Draft to Backlog or Active, or from Backlog to Active. Promote only lower
statuses. Preserve Assets, terminal statuses, and unpublished revisions
of Tickets that already have a Current carrier.

When a Ticket becomes Done or Canceled, cancel every Current descendant
whose Status is neither Done nor Canceled. Preserve the Status, Version,
and history of the other descendants.

Reopening a Done or Canceled planning Ticket makes it Active. Its descendants
keep their current Status, Version, history, and containment.

### Content

The Package Spec declares its Package ID in the Formal Claim. Its Purpose
and Contract remain authored in their Markdown sections. The Realization
uses its Spec Binding to identify the exact Spec revision.

### Materialized Views

The Atom ID, Header, Content, and declared Project Structure determine
the filename and location. The files and directories materialize that
placement. An Atom with children has a companion folder beside its file.
The folder uses the full filename without `.md`. Its children live inside
the folder and use the same rule for their own children. The authored
Container determines the owner. Destination and Ref ID are computed
values. Ref ID derives from Atom ID, Version, and Status. A Draft suffix
identifies a Draft revision.

The SPEC Lens uses the owning root. Prefix each named Lens directory
with two underscores. For example, Lens `DES/DOM` uses `__DES/__DOM/`.
The YAML Lens value and the filename Lens token use the Lens name.

### Migration

Apply this layout after the native tools can read and write it. Compare
migrated authored values to exact Git revisions through the migration
bindings. Restore admitted values and preserve evidence for unresolved
fields. Preserve Atom IDs, exact revision references, and Markdown Content
during a mechanical format migration.

## References

AN-T-2929, AN-S-3118, AN-S-2181, AN-S-3013, AN-S-3014.
