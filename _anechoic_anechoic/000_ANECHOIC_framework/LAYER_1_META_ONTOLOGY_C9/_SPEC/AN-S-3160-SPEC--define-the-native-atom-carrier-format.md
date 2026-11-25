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
  version: 16
  updated_at: '2026-11-22T12:51:17.372084+00:00'
---

## Summary

Define the native Atom Carrier format

## Claim

The Atom Carrier is the source of truth. The YAML Header carries the
Atom's Properties. The Markdown Content follows the Header.

### Header order

SPEC and TKT use this order:

1. `atom_family` is required. Use `SPEC` or `TKT`.
2. `atom_id` is required. Preserve its stable ID and numeric suffix.
   The S and T markers identify SPEC and TKT.
3. `concern` is optional. SPEC and Project Config use one locator with
   Subject, Path, and Relation. TKT uses a list of these locators.
4. `container` is a required top-level mapping with exactly one
   `component` or `atom` key and its owner's ID.
5. SPEC requires top-level integer `tier`. TKT requires top-level integer
   `priority`. Use Priority 2 for migrated and new Tickets.
6. `context` contains `template` first when present, then SPEC `lens`.
   TKT requires `template` and can add a navigation `label`.
7. `relations` is optional. Each authored Relation contains a list of
   stable Atom IDs or exact revision references.
8. `state` contains `status`, `version`, and `updated_at`, in that order.
   Write Status as a plain YAML scalar, for example `status: active`
   or `status: in_queue`.

Project Config Atoms use `atom_family: PROJECT_CONFIG` and C IDs. They
store their Container in `structure.container`. Their published
revisions require `context.template`.

The Project is the only Container for Axiom and Applicable Principle.
For Project-local SPEC, the Axiom Template uses the SPEC Lens and Tier 0.
The Contract Template uses Tier 0, and the Applicable Principle Template
uses Tier 1 or Tier 2.

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

A Component Seed Manifest has three Markdown sections. Formal Manifest
declares the Component Seed ID and any boundaries. Purpose and Solution
carry the authored prose. The Realization uses its Spec Binding to identify
the exact Manifest revision.

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

The Active Tier -1 Project Manifest and Goal use the repository root.
Active Tier 0 SPEC Atoms use their owning root. For Project-owned Tier 0
Atoms, this is the Project control directory.

The Project Manifest declares the folder layout for Active SPEC Atoms
in `project.folder_layout.active_spec_by_tier`. Tier 1 uses the declared
folder in the owning root. The default is `01_TIER_1_ARCHITECTURE/`.
This Tier contains Applicable Principles at Project scope and Solutions,
Standards, and Policies at Component scope.

Active SPEC Atoms at Tier 2 and above use Lens directories in their owning
root. Prefix the first Lens segment with one underscore. Use plain names
for sublenses. For example, Lens `DES/DOM` uses `_DES/DOM/` and
Lens `DES/IO` uses `_DES/IO/`. General SPEC uses `_SPEC/`.
A Tier 4 Component Manifest uses `_SPEC/` in its parent Component.
Use the authored Lens in the Header and its final segment as the filename
Lens token.

SPEC Drafts, Ready Atoms, and Archives use `01_draft/`,
`02_ready/`, and `09_archived/`, respectively.
The Project control root uses `__TICKETS/` and `__PROJECT_CONFIG/`.
The Project Config directory holds configuration files.

### Project Config catalog

- **Custom Model**
  - **Custom Nodes**
    - **Atom.** Shared properties, constraints, and lifecycle.
      - **SPEC Atom.** Templates such as Axiom and axes such as Tier and
        Lens.
      - **Ticket Atom.** Templates and Ticket-specific properties.
    - **Component**, including Project.
    - **Package**.
  - **Custom Relations.** Relation types and inverse names, allowed
    endpoints, cardinality, and classifications such as transitive
    and functional.
- **Project Workflows.** Local Release and Public Release, with their
  Steps and Actions.

Store the Project's Custom Model Manifests in
`__PROJECT_CONFIG/CUSTOM_MODEL/`. Use the `model_manifest` Template
and the Project as Container. The compiler admits Active Manifests
from this directory. Use `## Semantics` for the meaning and
`## Formal Manifest` for the eDSL. Keep the type, properties, and
constraints for one Template in its Manifest.

Attach properties, constraints, and classification axes to their Node
types. Add Node types such as Event Record or Ephemeral when the Project
extends them. Keep Component and Package Manifests with their owners.
Keep Project settings in the Project Manifest at the Project root.

### Migration

Apply this layout after the native tools can read and write it. Compare
migrated authored values to exact Git revisions through the migration
bindings. Restore admitted values and preserve evidence for unresolved
fields. Preserve Atom IDs, exact revision references, and Markdown Content
during a mechanical format migration.
Existing P IDs remain valid references to Project Config Atoms.

## References

AN-T-2929, AN-S-3118, AN-S-2181, AN-S-3013, AN-S-3014.
