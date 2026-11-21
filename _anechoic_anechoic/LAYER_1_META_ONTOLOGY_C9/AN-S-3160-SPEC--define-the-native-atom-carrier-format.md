---
atom_family: SPEC
atom_id: AN-S-3160
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 9
  updated_at: '2026-11-21T20:42:37.490360+00:00'
---

## Summary

Define the native Atom Carrier format

## Claim

The Atom Carrier is the source of truth. The YAML Header carries the
Atom's Properties. The Markdown Content follows the Header.

### Header order

SPEC and TKT use this order:

1. `atom_family` is required: SPEC or TKT.
2. `atom_id` is required. Preserve its stable ID and numeric suffix.
   Its S or T marker agrees with Atom Family.
3. `concern` is optional. SPEC can declare a Subject with Path and
   Relation, affected Components, or both. TKT uses one list of typed
   references, such as `component(id=C51)`. Reserve `@` for eDSL calls.
4. `container` is a required top-level mapping with exactly one
   `component` or `atom` key and its owner's ID.
5. SPEC requires top-level integer `tier`. TKT requires top-level integer
   `priority`. Use Priority 2 for migrated and new Tickets.
6. `context` contains `template` first when present, then SPEC `lens`.
   TKT requires `template` and can add a navigation `label`.
7. `relations` is optional. Each authored Relation contains a list of
   stable Atom IDs or exact revision references.
8. `state` contains `status`, `version`, and `updated_at`, in that order.

The Project is the only Container for Axiom and Applicable Principle.
Axiom requires Tier -1; Applicable Principle requires Tier 2. Project Contracts require Tier 0. PMETA
retains its existing Header representation.

The citing Atom authors `IS_REFERENCE`. Derive `HAS_REFERENCE` as the
inverse. Migrate `REFERENCES` with the same targets and direction.
Derive containment from `container`.

### SPEC lifecycle

A finalized Draft becomes Ready, with YAML Status `ready`. When
implementation starts, Ready becomes Active. When retired, Active becomes
Archived.

### Ticket lifecycle

Tickets progress from Draft to Backlog, then to In Queue at the branch
root. In Progress is ephemeral; YAML Status remains `in_queue` while work
is in progress. Planning Tasks, including their Labels, finish Done or
Canceled. Issues of every Template finish Resolved or Canceled.

A standalone Asset can finish Complete, with YAML Status `complete`,
and uses `08_complete/`.

Replacement by another Atom permits Archive from any state. Historical
revisions remain addressable.

### Ticket containment

A planning Ticket uses the Task Template and can contain planning Tickets
and Assets at every depth. Place new bound Assets in `ASSETS/` in the
owning Ticket's companion folder. TKT Assets holds unbound Assets.

The Label is for navigation in Workbench and derived filenames. AN-S-3176
declares its vocabulary. Default to `Subtask` for a Task under a Task and
`Sub-epic` for an Epic under an Epic. An explicit Label takes precedence.

Changing a planning Ticket preserves its containment tree at every depth.
Move its companion folder with the Ticket when its path changes.

Promote contained planning Tickets recursively when their parent moves
from Draft to Backlog or In Queue, or from Backlog to In Queue. Promote
only lower statuses. Preserve Assets, terminal statuses, and unpublished
revisions of Tickets that already have a Current carrier.

When a planning Ticket becomes Done or Canceled, cancel every Current
nonterminal descendant. Preserve the Status, Version, and history of
terminal descendants, including Resolved Issues and Archived Tickets.

Reopening a Done or Canceled planning Ticket makes it In Queue. Its
descendants keep their current Status, Version, history, and containment.

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
identifies a Draft revision. A bare ID selects Current; `ID@Version`
selects an exact Current or Archived revision; `ID@Version-draft` selects
an exact Draft. Resolve a collision before archiving a Draft.

Use the corresponding Ref ID as the filename marker, followed by the
family-specific Lens and Template or navigation Label tokens and
`--<summary-slug>.md`. Form the slug from lowercase ASCII alphanumeric
runs joined by hyphens. Preserve the authored Summary.

Active SPEC Atoms at Tiers 0, 1, and 2 use the Component owning root,
regardless of Lens. The Project Tier -1 Manifest, Goal, and Axioms use
the Project root. SPEC Drafts, Ready Atoms, and Archives use `01_draft/`,
`02_ready/`, and `09_archived/`, respectively.
The Project control root uses `001_TICKETS/` and `002_PROJECT_CONFIG/`.

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
