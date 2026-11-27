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
  version: 38
  updated_at: '2026-11-26T18:34:31.644797+00:00'
---

## Summary

Define the native Atom Carrier format

## Claim

The authoritative Atom Carrier stores a YAML Header followed by Markdown Content. Any additional Carrier follows its applicable declaration and represents the same revision.

Preserve exact IDs, opaque references, authored text, and typed values. The YAML Header carries metadata. Markdown carries Summary and the other Content Properties in their defined sections. Store each property value once at its declared location.

Write each YAML mapping key once. A scalar uses its declared type. Use plain scalars for registered YAML-safe controlled strings.

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

Derive containment from `container`.

### Additional Status placement

An In Queue Ticket uses its branch root. A standalone Complete Asset uses
`08_complete/`. A Status subdirectory serves only as a placement group.
Read the Atom’s Status from its Header. Historical revisions remain addressable.

### Ticket containment

A planning Ticket uses the Task Template and can contain planning Tickets
and Assets at every depth. Place new bound Assets in `ASSETS/` in the
owning Ticket's companion folder. TKT Assets holds unbound Assets.

The Label is for navigation in Workbench and derived filenames. AN-S-3176
declares its vocabulary. Default to `Subtask` for a Task under a Task and
`Sub-epic` for an Epic under an Epic. An explicit Label takes precedence.

### Content

A Project Manifest or Component Manifest may include a `## Purpose` section.

A Component or Component Seed exists when an Active Manifest formally
declares its identity. A Component Seed Manifest requires one `## Formal Manifest`
section for its ID and any boundaries. It may include nonempty Purpose,
Contract, and Solution sections after it, in that order. The Realization
uses its Spec Binding to identify the exact Manifest revision.

### Materialized Views

The Atom ID, Header, Content, and declared Project Structure determine
the filename and location. The files and directories materialize that
placement. An Atom with children has a companion folder beside its file.
The folder uses the full filename without `.md`. Its children live inside
the folder and use the same rule for their own children. The authored
Container determines the owner. A Carrier has a placement discrepancy when its actual filename or location differs from the derived destination. Destination and Ref ID are computed
values. Ref ID derives from Atom ID, Version, and Status. A Draft suffix
identifies a Draft revision. A bare ID selects Current; `ID@Version`
selects an exact Current or Archived revision; `ID@Version-draft` selects
an exact Draft. Resolve a collision before archiving a Draft.

Use `ID` for a Current filename marker, `ID@Version` for an Archive,
and `ID@Version-draft` for a Draft. Follow it with the
family-specific Lens and Template or navigation Label tokens in uppercase, followed by
`--<summary-slug>.md`. Form the slug from lowercase ASCII alphanumeric
runs joined by hyphens. Preserve the authored Summary.

The Active Tier -1 Project Manifest and any Active Tier -1 Project Goals use the repository root.
Active Tier 0 SPEC Atoms use their owning root. For Project-owned Tier 0
Atoms, this is the Project control directory. A Component's main Solution
uses Tier 0 and answers the exact revision of its Component Manifest.

The Project Manifest declares the folder layout for Active SPEC Atoms
in `project.folder_layout.active_spec_by_tier`. Tier 1 uses the declared
folder in the owning root. The default is `01_TIER_1_ARCHITECTURE/`.
This Tier contains Applicable Principles at Project scope. At Component
scope it contains Manifests for child Components, Standards, and Policies.
The Manifest Header identifies the declaring parent. Component Identity is
the only required Component Manifest section. Purpose, Component Boundaries,
and Component Contract are optional.

Active SPEC Atoms at Tier 2 and above use Lens directories in their owning
root. Prefix the first Lens segment with one underscore. Use plain names
for sublenses. For example, Lens `DES/DOM` uses `_DES/DOM/` and
Lens `DES/IO` uses `_DES/IO/`. General SPEC uses `_SPEC/`.
Use the authored Lens in the Header and its final segment as the filename
Lens token.

SPEC Drafts, Ready Atoms, and Archives use `01_draft/`,
`02_ready/`, and `09_archived/`, respectively.
The Project control root uses `__TICKETS/` and `__PROJECT_CONFIG/`.
The Project Config directory holds configuration files. Keep the repository's `LICENSE` and any `LICENSES/` notices outside the Project control and runtime directories.

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
    endpoints, cardinality, and Axes such as Transitive
    and Functional.
- **Project Workflows.** Local Release and Public Release, with their
  Steps and Actions.

Store Project Custom Model Manifests in `__PROJECT_CONFIG/CUSTOM_MODEL/` with the Project as Container. Admit Active `manifest_node`, `manifest_property`, and `manifest_relation` Templates there. During migration, continue to admit Active `model_manifest` carriers.

A Continuant Node may omit its Formal Manifest when its Concern declares containment and its Subject is a Python identifier. For a Node with no formal rules, use `node(Name)` or `node(Name, Base, ...)` if the Concern alone cannot preserve its Python name or bases. Use a class for additional formal rules. Each other typed Manifest has one `python anechoic-edsl` fence under `## Formal Manifest`. A typed Custom Model declaration may use a Concern to locate its Model subject. Use `## Semantics` for meaning when needed; it is optional. Continuant Declarations use DOM/CONT with Declarative Control Flow. Their Header requires one Concern. Use the declared Subject name and its parent Path in the Model tree. The Relation states how the Subject joins that Path. Exclude Draft and Archived carriers from active Model admission.

Use `node.parts` to name a Node’s canonical subparts or link to another
declared Node. A key prefixed with `=>` links to the target’s canonical
definition. Use `node.alternatives` to declare the part lists that each
containment view displays. Use `node.aliases` for alternate names of the
same canonical Node.

Attach Properties, constraints, and Axes to their Node
types. Add Node types such as Event Record or Ephemeral when the Project
extends them. Keep Component and Package Manifests with their owners.
Keep Project settings in the Project Manifest at the Project root.

### Migration

Apply this layout after the native tools can read and write it. Compare
migrated authored values to exact Git revisions through the migration
bindings. Restore admitted values and preserve evidence for unresolved
fields. Preserve Atom IDs, exact revision references, and Markdown Content
during a mechanical format migration. A Carrier-only recoding preserves the authored Claim, applicability, and direct Relations.
Existing P IDs remain valid references to Project Config Atoms.

## References

AN-T-2929, AN-S-3118, AN-S-3175, AN-S-3013, AN-S-3014.
