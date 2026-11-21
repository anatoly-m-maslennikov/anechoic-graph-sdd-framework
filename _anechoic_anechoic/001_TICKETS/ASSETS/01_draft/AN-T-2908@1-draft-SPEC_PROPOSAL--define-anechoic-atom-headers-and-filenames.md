---
atom_family: TKT
atom_id: AN-T-2908
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

The Atom Carrier contains YAML frontmatter followed by Markdown Content.
The Header is the frontmatter. Use this order for SPEC and TKT:

1. `atom_family` is required. Use SPEC or TKT.
2. `atom_id` is required. Store the stable ID at the top level. Its S or T
   marker must agree with Atom Family. Preserve the numeric suffix,
   including leading zeros.
3. `concern` is optional. A SPEC Concern can state a Subject with its
   Path and Relation, affected Components, or both. A TKT Concern uses a
   single list of typed references such as `[component(id=C51)]`.
   Reference kinds share this list. Reserve `@` for eDSL function calls.
4. `container` is required at the top level. Use one mapping with exactly
   one `component` or `atom` key and the owner's ID.
5. SPEC requires top-level integer `tier`. TKT requires top-level integer
   `priority`. Use Priority 2 for migrated and new Tickets.
6. `context` contains `template` first when present. SPEC stores `lens`
   next. TKT requires `template` and can add a navigation `label`.
   Planning Tickets use the Task Template, including Epic and Subtask.
7. `relations` is optional. Each authored Relation has a list of stable
   Atom IDs or exact revision references as targets.
8. `state` contains `status`, `version`, and `updated_at`, in that order.

### Project-local SPEC Templates

- Contract uses Tier 0 (`template: contract`).
- Applicable Principle uses Tier 2.
- Supporting Principle is proposed. Its Tier is open.

The Project is the Container for these Templates. Spec Proposal is a
Ticket Asset. A PKG Spec declares its Package ID in its Formal Claim.

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

Attach properties, constraints, and classification axes to the Node
type they apply to. Add other Node types, such as Event Record or
Ephemeral, when the Project extends them.

Component and Package Manifests stay with their owners. The Project
Manifest at the Project root holds identity, paths, enabled Lenses, and
runtime parameters.

Axiom Atoms use the SPEC Lens and Tier -1. Their only Container is the
level 0 Project. Their files live at the Project root and in its
lifecycle status directories.

### SPEC example

```yaml
atom_family: SPEC
atom_id: AN-S-3190
container:
  component: C00
tier: 2
context:
  template: applicable_principle
  lens: SPEC
relations:
  IS_REFERENCE:
    - AN-S-1432
state:
  status: active
  version: 1
  updated_at: '2026-11-21T18:00:00+00:00'
```

### TKT example

```yaml
atom_family: TKT
atom_id: AN-T-2960
concern:
  - component(id=C51)
container:
  atom: AN-T-2959
priority: 2
context:
  template: task
  label: Task
state:
  status: active
  version: 2
  updated_at: '2026-11-21T18:00:00+00:00'
```

### SPEC lifecycle

1. A SPEC Atom starts in Draft (`draft`, `01_draft/`).
2. Finalization moves it to Ready (`ready`, `02_ready/`).
3. Implementation start moves it to Active (`active`), using Active
   placement for its Lens and Tier.
4. Retirement moves it to Archived (`archived`, `09_archived/`).

Ready is a Current revision. Use the stable ID in its filename and the
exact ID and Version for a revision reference.

### TKT lifecycle

A Ticket moves from Draft to Backlog, then In Queue (`in_queue`) at its
branch root. Backlog is the TKT counterpart of SPEC Ready. In Progress
is ephemeral. Keep `in_queue` in the Header while work is in progress.

Planning Tickets, including Epics and Tasks, finish Done or Canceled.
Issues finish Resolved when a disposition is recorded or Canceled when
withdrawn. Standalone Assets finish Complete (`complete`), such as an
Analysis Report whose document is complete. A replacement by another
Atom can archive a Ticket from any
state. Revisions already in Archive retain their exact references.

### References and filenames

The citing Atom stores the direct `IS_REFERENCE` edge. Derive the inverse
`HAS_REFERENCE` on the cited Atom. Migrate existing `REFERENCES` entries
with the same targets and direction. Derive containment from `container`.

A bare ID selects Current. `ID@Version` selects the exact Current or
Archived revision. `ID@Version-draft` selects the exact Draft. The Draft
suffix distinguishes an unpublished revision from an Archive with the
same version. Resolve a collision before archiving a Draft.

Derive Ref ID, filename, and location. Use `ID`, `ID@Version-draft`,
or `ID@Version` as the filename marker for Current, Draft, or Archive.
Then apply the family-specific Lens and Template or navigation Label
tokens. End with `--<summary-slug>.md`. Form the slug from lowercase ASCII
alphanumeric runs joined by hyphens. Preserve the authored Summary.

### Carrier directories

- At a Component's owning root, place Current SPEC Atoms at Tiers 0, 1,
  and 2 directly at the root when Active. Keep the authored Lens and its filename
  token. Other Atoms use the existing subfolder rules, including named
  Lens directories such as `__DES/`, `__DEVOPS/`, `__QA/`, and `__SWD/`.
  Drafts and Archives use `01_draft/` and `09_archived/`. Keep the
  Project's Tier -1 Manifest, Goal, and Active Axioms at the Project root.
- At the Project control root, use `001_TICKETS/` for Tickets and
  `002_PROJECT_CONFIG/` for configuration files. Project Config Atoms
  use `atom_family: PROJECT_CONFIG` and C IDs.
- TKT uses the `TASKS/`, `ISSUES/`, and `ASSETS/` branches below
  `001_TICKETS/`. In Queue records live at their branch root. Use
  `01_draft/`, `09_archived/`, or the applicable status directory.
- A containing Atom has a companion directory beside its Markdown file.
  The directory uses the full filename stem. Apply the rule recursively.
  Place attached Ticket Assets in the owning Task or Epic's `ASSETS/`
  directory. Place detached Assets in the Project's `001_TICKETS/ASSETS/`.
  Completed standalone Assets use that branch's `08_complete/`.

### Adoption

AN-T-2959 owns the sequence. Finalize the SPEC and TKT Header and Model
rules in AN-T-2960, migrate carriers in AN-T-2964, then revise the
lifecycle backend and MCP.

Preserve Atom IDs, exact revision references, and Markdown Content during
mechanical migration. Convert existing TKT `active` to `in_queue` and
preserve `resolved` on Issues. Convert `done` standalone Assets to
`complete`. Recover authored values from Git where
available.
Map the legacy Tier `core` to Tier 1. Assign Tier 2 only where no authored
Tier can be recovered. Record the source of each recovered or defaulted
Tier and any unmapped values. Record original
paths and digests in the migration receipt.

When an authored timestamp is missing or has no timezone, use the captured
file modification time in UTC and retain both values in the receipt. When
a legacy carrier has an opening title and no Summary, add the title as
the Summary and preserve the original Markdown bytes below it.

For approved unnumbered legacy Archives, use separate IDs and retain each
stored Version. Map each original path to its exact reference. For a
withdrawn legacy Draft migrated to Archive, preserve its original
Draft-qualified reference in the migration map.

## References

AN-T-2959, AN-T-2960, AN-T-2964, AN-T-2965, AN-S-3160, AN-S-3117,
AN-S-3176, AN-C-3193, AN-S-3196, AN-S-3199.

Earlier migration inputs are CA-C-746, CA-P-3087, CA-P-3075, CA-A-1461,
CA-A-1462, CA-A-1463, and CA-A-1465.
