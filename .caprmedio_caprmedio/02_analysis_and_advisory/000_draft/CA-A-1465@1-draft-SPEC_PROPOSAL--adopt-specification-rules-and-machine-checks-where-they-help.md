---
identity:
  atom_id: CA-A-1465
  ref_id: CA-A-1465@1-draft
context:
  container:
    scope_unit: CA-SU-00
  role: analysis_and_advisory
  form: Spec Proposal
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO
  tier: 3
state:
  status: draft
  version: 1
  updated_at: '2026-11-16T21:31:37.203053+00:00'
destination:
  file:
    name: CA-A-1465@1-draft-SPEC_PROPOSAL--adopt-specification-rules-and-machine-checks-where-they-help.md
    path: .caprmedio_caprmedio/02_analysis_and_advisory/000_draft
---
## Summary

Adopt specification rules and machine checks where they help

## Proposal

Start with a Manifest and use concise Decisions and Standards when they help.
Add Purpose, Contracts, Demands, layers, Solutions, and Policies as the work
needs them. The Operator decides when to split or tighten the Specification.

### Configure rules in Manifests

The Tier −1 Project Manifest sets defaults and stays within 20 parameters.
A Component Manifest can override governance settings, declare a lens under an
unused Project-wide name, and choose eligible lenses for the Component it
describes. Refer to existing lenses by name. The effective lens whitelist comes from the
closest Manifest that defines one, starting with the Manifest for the Component
itself. That list replaces all higher lists.
An explicit empty list clears inherited lenses. With no declared list in
the ancestry, the Component has no enabled lenses. The effective whitelist
must list `SPEC` for it to be available. A Component can enable a lens and
any selection of its narrower lenses. Enabled sibling lenses must have
disjoint sets of detailed lenses. Keep Manifests and Purposes in SPEC. Keep internal
Project procedures and local meta-model extensions in PMETA. Use Markdown with Python eDSL blocks
built on predefined dataclasses and functions for machine-readable settings.
Validation reports invalid declarations with the reason and preserves the
authored values.

Represent source facts in the Atom carrier and compute reference IDs, physical
locations, and inverse relations as derived values. Semantic links can use stable
IDs. Lineage and version-pinned bindings use exact IDs and versions.
Carry forward legacy authored relations with verified declarations and
map their endpoints. Keep the Atom-tier `child_of` meaning as
`TIER_CHILD_OF`, distinct from Component `CHILD_OF`. Hold relations
whose declaration or endpoint cannot be verified. Apply
the family-ID migration to Archived, Current, and Draft revisions in that
order. Apply CA-A-1462's per-family numbering and filesystem ordering to
Spec, Ticket, and Project Meta Atoms. Rewrite stored references using
the migration map and preserve the version each reference pins. An exact legacy `CA-…@version` reference resolves to the same
revision through that map. When one legacy reference names revisions of
distinct lineages, retain both under separate new Atom IDs. Use the original
source path to select the intended revision. Convert each legacy Scope Unit ID to a Component
ID using its existing number, as in `CA-SU-43` → `C43`. Final Header fields
and the filename formula need their own review before migration.

Before moving files, capture the legacy source inventory selected by the
current Local Release. Keep those inputs at their existing paths until the
Anechoic build takes over. Preserve their filenames, IDs, revisions, and
contents. Include the Project Settings and Scope Unit structure used to
select them, plus pinned inputs such as the lifecycle Workflow, Step, and
Action.

Keep both source sets in parallel throughout the full migration. Local
Release uses the legacy inputs. Each migrated batch enters the Anechoic
source set under its new paths, filenames, and IDs. After the move, compare the legacy release
selection with the pre-move inventory and verify the rebuild. Verify the
Anechoic index against the migrated source set separately.

Prioritize a fast mechanical move of all legacy Methodology Atoms to
Meta-ontology. Apply the migration whitelist from CA-A-1462 and preserve the
existing claims and Control Flow values. Review and fix the migrated Atoms,
including moves to Meta-methodology, in a separate pass.

### Make Summary rigor configurable

In casual use, a Summary can name the topic within the current Lens. In strict
use, the Summary includes the Claim and the Atom contains the Claim and its
supporting details. Use a separate Concern where it improves navigation.

### Add evidence where it helps

Start with the link between a Component Spec Section and its Component Package.
Use sidecar bindings for relevant packages and boundary modules. List Standards
as applied at the Component Package. Their scope covers that Component’s
Realization and all descendant Components.

Defer Spec Atom implementation statuses such as shipped and pending, along
with full Decision coverage checks.

Sidecars record trace bindings to Realization. Use CA-A-1463 for explicit
and filename-based boundaries. Import reachability can help inspect unpinned
modules. Mapped passing tests provide evidence for the behavior they exercise.
Use Operator-selected review gates or locks where needed.

Look at measurable agent friction in a review: how many Atoms an agent reads to
find one detail, how much text it reads for that detail, and how often it uses
full-text search. Use these signals to propose changes such as splitting a broad
Atom or improving retrieval. The Operator decides when to change the rules.
The ice and entropy language describes relative structure and can explain why
different Components use different amounts of rigor.

### Source notes

Gemini transcript lines 17912–17976, 18643–18708, 20063–20085, 20301, 21055,
21263–21349, 21990–21994, and 22248–22281.
Second brainstorm, lines 4, 17, 27, 62, 533, and 852.
Third brainstorm, lines 1500, 1742, 1894, 2476, and 2569.
Fourth brainstorm, line 1492.
