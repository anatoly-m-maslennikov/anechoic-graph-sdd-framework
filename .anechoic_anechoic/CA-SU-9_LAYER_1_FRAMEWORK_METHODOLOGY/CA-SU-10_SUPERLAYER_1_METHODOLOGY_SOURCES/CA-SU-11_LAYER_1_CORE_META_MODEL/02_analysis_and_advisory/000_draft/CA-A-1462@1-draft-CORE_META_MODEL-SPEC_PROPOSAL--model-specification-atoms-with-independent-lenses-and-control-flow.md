---
identity:
  atom_id: CA-A-1462
  ref_id: CA-A-1462@1-draft
context:
  container:
    scope_unit: CA-SU-11
  role: analysis_and_advisory
  form: Spec Proposal
  topics:
    main_subject: MODEL//ANECHOIC <+ Atom
  tier: 3
state:
  status: draft
  version: 1
  updated_at: '2026-11-16T21:31:29.966056+00:00'
destination:
  file:
    name: CA-A-1462@1-draft-CORE_META_MODEL-SPEC_PROPOSAL--model-specification-atoms-with-independent-lenses-and-control-flow.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/02_analysis_and_advisory/000_draft
---
## Summary

Model Specification Atoms with independent lenses and control flow

## Proposal

Treat the Specification as one document made of Atoms. An Atom is an independently
addressable, versioned contribution. Its Concern identifies what it addresses.

### Component, Tier, and Lens

- **Component** identifies the Component containing the Atom, directly or
  through an enclosing Atom. The `child_of` relation points from a Component
  to its direct `parent` Component. The parent's `children` are the inverse.
- **Container** locates an Atom in a Component or another Atom. The
  `contained_by` relation points from the Atom to its `container`.
  For example, a Task is `contained_by` its Epic.
- **Tier** locates the Atom within its containing Component’s hierarchy.
  The Project Manifest and Project Goal are Tier −1. Tier 1 Axioms state
  accepted truths. Tier 2 Applicable Principles guide choices.
- **Lens** is a named, optional grouping of viewpoints. The Operator chooses
  its name, composition, and granularity.

A lens name has one meaning across the Project. A Component can declare a new
lens under a name unused in the Project. Use existing lenses by reference.
Wherever a lens is enabled, it resolves to the same detailed lenses. Policy
filters rely on that shared meaning across Components.

Each Component has an effective lens whitelist. Use the list in the
Manifest that describes the Component when that Manifest supplies one.
Otherwise, use the closest ancestor's declared list.
That list replaces all higher lists as a whole. An explicit empty list clears
inherited lenses. With no declared list anywhere in the ancestry, the Component
has no enabled lenses. `SPEC` is available when the effective whitelist lists it.
For the mechanical migration, write `lens_whitelist` explicitly on each
migrated Component Manifest from the lenses used by its mapped Atoms.
Enable `SPEC` explicitly at the Project root for the Project Manifest and
Goal. Keep the approved temporary Meta-ontology admissions for its first pass.

Lenses use the `narrower_than` relation. A Component can enable a broader
lens together with any selection of its narrower lenses. A narrower lens is
separately available when listed in the whitelist. Every other lens is
narrower than `SPEC`, so `SPEC`, `DES`, and `SWE` can be enabled together.
A Component can enable `SWE`, `SWD`, and `QA` while omitting DevOps.

Enabled sibling lenses must have disjoint sets of detailed lenses.
`DES` (`IO + DOM`) and `SYS` (`SWE + DOM`) both include `DOM`. Reject a
Component whitelist that enables both.

Use **architecture viewpoint** in the strict ISO/IEC/IEEE 42010 sense: conventions
for making and interpreting architecture views that address specified concerns.
A Lens groups viewpoints for navigation and retrieval. Use the viewpoints relevant
to the work.

### Canonical lenses

Anechoic uses the following lens names and groupings. The referenced
standards give definitions for the underlying concepts. The project
uses those concepts to choose what belongs in each lens.

| Lens | Definition in Anechoic | Standards concept |
|---|---|---|
| `SPEC` — Specification (`DES` + `SWE`) | The expected properties, behavior, and constraints of the Realization. It also covers general Spec claims that span the two branches. | A software requirements specification records required functions, performance, attributes, constraints, and external interfaces. [ISO/IEC/IEEE 29148:2018, requirements and software requirements specification](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec-ieee%3A29148%3Aed-2%3Av1%3Aen) |
| `DES` — Design (`IO` + `DOM`) | The product as intended, including observable interfaces and behavior and the domain rules behind them. | System design specifies the elements and relationships needed to realize the architecture. [ISO/IEC/IEEE 29148:2018, requirements engineering](https://www.iso.org/standard/72089.html) and [ISO/IEC/IEEE 15288:2023, system life-cycle design processes](https://www.iso.org/standard/81702.html) |
| `IO` — Interfaces and interaction | What people and external callers can observe, send, or receive through a UI, a public API such as MCP, or exposed data and events. | A UI supplies information and controls to people. An API supplies defined means for software to access features or data. [ISO 9241-220:2019, user interface and user experience](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso%3A9241%3A-220%3Aed-1%3Av1%3Aen) and [ISO/IEC/IEEE 26514:2022, application programming interface](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec-ieee%3A26514%3Aed-1%3Av1%3Aen) |
| `DOM` — Domain | The subject area's concepts, rules, invariants, and processes that determine expected behavior across interfaces. | A domain is a distinct subject area. TOGAF's Business and Data Architecture domains supply related framing. [ISO 19146:2018, domain terminology](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso%3A19146%3Aed-2%3Av1%3Aen) and [The Open Group, TOGAF architecture domains](https://help.opengroup.org/hc/en-us/articles/32115987894930-How-the-ArchiMate-Language-and-the-TOGAF-Standard-Complement-Each-Other) |
| `SWE` — Software Engineering (`SWD` + `QA` + DevOps) | The engineering practices and decisions used to design, build, verify, deliver, operate, and maintain software. | Software engineering applies disciplined, measurable practices to software development, operation, and maintenance. [IEEE SWEBOK v4, software engineering](https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf) and [ISO/IEC/IEEE 12207:2026, software life-cycle processes](https://www.iso.org/standard/90219.html) |
| `SWD` — Software Design (`SWA` + `SWS`) | The software's intended internal structure and implementation constraints. | Software design specifies how software will be structured, from high-level design to detail. [IEEE SWEBOK v4, Software Design knowledge area](https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf) |
| `SWA` — Software Architecture | The software's fundamental elements, relationships, and design principles that guide its evolution. | An architecture expresses the fundamental concepts and properties of an entity in its elements, relationships, and principles. [ISO/IEC/IEEE 42010:2022, architecture description](https://www.iso.org/standard/74393.html) and [IEEE SWEBOK v4, Software Architecture knowledge area](https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf) |
| `SWS` — Software Standards | Binding, repeatable rules for software design and construction, such as code structure and coding conventions adopted as standards. | A standard sets rules or characteristics for repeated use and is adopted through consensus and approval. [ISO/IEC Guide 2, definition of standard](https://policy.iso.org/resources.html) |
| `QA` — Quality Assurance | The practices and evidence that provide confidence that quality requirements will be met. This lens includes verification, validation, testing, and evaluation. | Quality assurance is the part of quality management that provides confidence that quality requirements will be fulfilled. [ISO 9000:2015, §3.3.6, reproduced in ISO/IEC 29110-7-1:2026](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec%3A29110%3A-7-1%3Aed-1%3Av1%3Aen) and [IEEE SWEBOK, Software Quality](https://www.computer.org/education/bodies-of-knowledge/software-engineering/topics) |
| **DevOps** | Development and operations practices for reliable and secure delivery and operation. The lens covers CI/CD, build and packaging, environments, infrastructure, and runtime enablement. | DevOps integrates development, operations, and other stakeholders to improve software life-cycle processes. [ISO/IEC/IEEE 32675:2022, DevOps](https://www.iso.org/standard/83670.html) |

A Component can refine IO into interface design, interaction, and visual
design. User experience describes people's perceptions and responses to
use. Frontend or Backend can be additional project-defined groupings.
A `Standard` template can be used in any applicable lens. `SWS` covers
standards for software design and construction.

Meta-ontology enables `DES` and its `DOM` sublens (`DES/DOM`). Its Control
Flow Model is Declarative. Meta-methodology enables `DOM` and uses the
Imperative Control Flow Model.

Standards are mandatory. Conventions are advisory. `docs/` describes the system
as built and can record exact commands, API methods, and usage.

### Concerns

Use the Component tree for structural Concerns. A child Component’s Purpose
and Manifest are Atoms in the parent Component. The child they describe
supplies their structural Concern. A Contract can use its containing Component
as its implicit Concern. Use the separate Concern tree for shared subjects
such as `engineering/concurrency` or `Model/Graph/Node//Artifact//atom`.
Multiple Components can specify different aspects of one Concern.

Use three fields for an explicit Concern.

- `concern.path` identifies the full existing path in short notation, such
  as `Model/Graph/Node//Artifact`. Include every intermediate type.
- `concern.subject` names what the Atom addresses, such as `atom`.
- `concern.relation` gives the relation name from the subject to the path.
  Use snake case.

```yaml
concern:
  path: "Model/Graph/Node//Artifact"
  subject: atom
  relation: narrower_than
```

In `Model/Graph/Node//Artifact`, each `/` expresses containment and
`//` says that Artifact is narrower than Node. Atom `contained_by` records
its container, which can be a Component or another Atom.

Use `<+` for composition from whole to part, `.` for a property, and
`::` for allowed values.
The part-to-whole example is `step < workflow`. Classification groups
flat values for applying rules. Express classification through named
relations.

### Migrate Topics to Concerns

Migrate Topics mechanically in the Anechoic copies of Current, Draft, and
Archived revisions. Translate `topics.main_subject` to the primary Concern
using the old address’s original semantics. When it lists several primary
subjects, use the first in stored order. Drop `topics.dependencies`. Apply
the family ID mapping and preserve each revision’s version.

If the legacy subject has no complete path that can be mapped mechanically,
leave the Concern unset in the migrated copy. Record the source reference
and original subject verbatim in the migration report. Resolve it during
the later cleanup pass.

### Primary entities

```text
model/graph
model/graph/node
model/graph/relation
model/eDSL
model/carrier

node//artifact
node//ephemeral

artifact//atom
atom//spec_atom
atom//ticket_atom
atom//pmeta_atom
artifact//event_record

artifact//component
component//project
component <+ component_spec_section
component <+ component_package

artifact//package
package//component_package
package <+ package
package <+ module
module <+ unit
```

Graph consists of Nodes and Relations. Concern notation gives selected
Relations short spellings. The eDSL is the Python language used to write
Manifests. Format and Cardinality belong to the eDSL. SPEC defines the
model and contains Project and Component Manifests and Purposes. PMETA
contains the Project’s local meta-model, including extensions such as
specialized Component types.
**View** is the new name for the Current **Projection**. A model View
presents derived information from source Atoms and relations. The Workbench
model owns Workspace and its editable SQL View.

Artifact and Ephemeral are the main branches under Node. Continuant,
Occurrent, and SSOT are classifications expressed through named relations.

| Classification | Members specified here |
|---|---|
| Continuant | Spec Atom, PMETA Atom |
| Occurrent | Ticket Atom |
| SSOT | Spec Atom, Event Record |

| Legacy Atom branch | Proposed home |
|---|---|
| Requirement (R) | SPEC / Design (DES), the combined IO and DOM lens. |
| Method (M) | SPEC / Software Design (SWD). |
| Evaluation (E) | SPEC / QA. |
| Delivery (D) | SPEC / DevOps. |
| Concern, Analysis and Advisory, Plan | TKT for issues, analysis, and plans for a case of work. |
| Archived Implementation (I) | TKT / Issue / Code-Spec Mismatch. Preserve Archived status, contents, and revision history. |
| Operations | Product and Engine behavior in SPEC. Reusable Project procedures in PMETA. |

Map R, M, E, and D to their target lenses mechanically. Assign all legacy
Requirements to `DES`, whose detailed lenses are `IO` and `DOM`.

Prioritize a fast mechanical migration. Move all legacy Methodology Atoms to
Meta-ontology first. Preserve their claims and existing Control Flow values.
During this pass, Meta-ontology accepts `DES`, `DES/DOM`, `SWD`, `QA`,
and DevOps. Map `M` to `SWD`, `E` to `QA`, and `D` to DevOps.
Review and fix the migrated Atoms in a separate pass, including moves to
Meta-methodology and applying the final Component rules.

Migrate a linked legacy Step or Action to the family (`SPEC` or `PMETA`) of
the Workflow that uses it. Use `DES/DOM` for Atom lifecycle Workflows and
their linked Steps and Actions. Assign a legacy Step or Action without a Workflow
link to PMETA and give it an `AN-P` ID. Preserve existing links through the
migration map and leave unlinked Steps and Actions unlinked.

PMETA retains Workflow, Step, and Action as Atom types. A Step or Action can
have its own `AN-P` ID. Review the remaining Current entities against the
proposed types before assigning their new placement.

### Current primary-entity reference

The list below records the 96 Current formal entity declarations. It uses the
proposed `//` spelling to show existing narrowing relationships. The Current
notation also declares CFEL and its Operator, linked by composition
(`CA-R-2487@16`, `CA-R-2616@3`).

```text
cardinality
carrier
carrier//database
carrier//directory
carrier//docker_image
carrier//file
file//markdown
markdown//markdown_atom_carrier
carrier//git_branch
carrier//git_commit
carrier//git_repository
carrier//pull_request
format
format//bool
format//datetime
format//decimal
format//float
format//int
format//scalar
format//string
node
node//aspect
node//continuant
continuant//actor
continuant//atom
atom//analysis_and_advisory
atom//concern
concern//code_spec_mismatch
atom//delivery
delivery//decision
delivery//eng_standard
delivery//file_layout
delivery//solution
delivery//spec_policy
atom//evaluation
evaluation//decision
evaluation//eng_standard
evaluation//solution
evaluation//spec_policy
atom//method
method//decision
method//eng_standard
method//solution
method//spec_policy
method//term_definition
atom//operations
operations//action
operations//decision
operations//step
operations//workflow
atom//plan
plan//plan_form
plan//work_report
atom//requirement
requirement//declaration
requirement//relation_declaration
requirement//requirement_form
requirement//scope_unit_declaration
requirement//solution
requirement//spec_policy
continuant//event_record
continuant//journal
continuant//named_selection
continuant//package
package//project_package
continuant//projection
projection//catalog
projection//entity_definition_and_active_subject_coverage
projection//hub
projection//map
projection//passive_only_subjects
projection//primary_entities_tree
projection//primary_entities_with_direct_properties
projection//primary_entities_with_inherited_formal_claims
projection//primary_entities_with_inherited_property_contracts
projection//subjects_without_requirement_declarations
continuant//scope_unit
scope_unit//project
node//model
node//occurrent
occurrent//event
occurrent//execution
execution//action_run
execution//step_run
execution//workflow_run
occurrent//runtime
runtime//external_local_runtime
runtime//external_remote_runtime
external_remote_runtime//session
runtime//internal_local_runtime
runtime//internal_remote_runtime
node//project_structure
relation
term
view
workspace
```

Baseline declarations: Node `CA-R-2462@9`, Relation `CA-R-2247@16`, Continuant
`CA-R-2589@4`, Occurrent `CA-R-2590@4`, Atom `CA-R-2508@15`, Scope Unit
`CA-R-2523@6`, and Project `CA-R-2524@7`.

### Identity and lens changes

An Atom ID uses `<project prefix>-<S/T/P>-123`. Spec, Ticket, and Project
Meta Atoms use `S`, `T`, and `P` respectively. An Atom retains its
family. A filename can add a template or lens suffix, as in
`AN-S-123-DECISION` or `AN-S-123-BACK`. Apply the family ID mapping to the
full Atom history, including Archived revisions. Rewrite stored references
to the corresponding revisions under their new IDs. An exact legacy
`CA-…@version` reference resolves to the same revision through the mapping.

Freeze one Project-wide source inventory and ID map before moving files.
Record each file’s original path and modification time. Every migration
batch uses the frozen map.

Assign new numbers from separate Project-wide sequences for Spec Atoms
(`AN-S`), Ticket Atoms (`AN-T`), and Project Meta Atoms (`AN-P`).
In each sequence, process Archived files first, then Current files, then
Draft files. Within each group, order files by the captured modification
time, oldest first. Use the original path for equal times. Assign
the new ID on the first encounter of a numbered legacy Atom and reuse it
for all its revisions. If a legacy ID was used for distinct confirmed
lineages, allocate each lineage separately and preserve its versions.
Require the original source path for an ambiguous exact legacy reference.
Use the original path to distinguish unnumbered Drafts that share a
placeholder ID.

The **bound** axis distinguishes Specification about Realization from
Project meta-model and Workflow definitions and individual cases of work.

| Atom family | Bound |
|---|---|
| Spec Atom | Matter-bound (Realization) |
| PMETA Atom | Matter-bound (Project) |
| Ticket Atom | Time-bound |

SPEC, PMETA, TKT, and REAL are the Project’s four top-level logical trees.
SPEC holds `AN-S` Atoms, PMETA holds `AN-P` Atoms, and TKT holds `AN-T` Atoms.
REAL holds Realization files. See CA-A-1461 for the filesystem roots.

In the Console, mechanical lens renames and regrouping preserve Atom claims
and links. A change that splits a claim uses reviewed Drafts and normal lineage.

### Control Flow Model and templates

Every normative lens can use **Declarative** requirements that state what must hold
and **Imperative** requirements that give a process or graph of actions. An Imperative
process can call another process. A Python Manifest uses the Declarative model.

A template can preset independent axis values and constrain the allowed local
tier. Claim format is `Formal | Prose`. A process can be programmatic, agentic,
or hybrid.

### Base Spec Atom templates

Decision, Standard, Solution, and Policy are templates for Spec Atoms.
The Package (`PKG`) template records a package ID, a short Purpose, and a
Contract in one Spec Atom. Use an allowed lens, as in
`AN-S-123-SPEC-PKG--lexer.md` or `AN-S-123-SWE-PKG--create-order.md`.
The Atom ID stays `AN-S-123` if the lens or name changes.
Template sets for PMETA and Ticket Atoms are open for separate design.

The **effect** axis states what a Spec Atom affects directly:
`Realization | Specification`.

| Template | Direct effect | Scope |
|---|---|---|
| Decision | Realization | A specific part of the owning Component’s Realization. |
| Standard | Realization | The whole Realization of the owning Component and all its descendants. |
| Solution | Specification | A design supported by other Solutions, Decisions, Standards, or Policies. |
| Policy | Specification | Spec Atoms selected by the Policy’s explicit `affects` property. |

A Solution can start without supporting Atoms. A supporting Solution, Decision,
Standard, or Policy declares `CONTRIBUTES_TO` toward the supported Solution.
An Atom can support more than one Solution. Support can cross Component
boundaries. For example, a Decision can support a Solution in a sibling
Component. Each explicit Atom-to-Atom relation has a derived reverse
endpoint for the same direct pair. For
example, if a Standard supports A and A supports B, B's reverse relation
points to A. A View can show the Standard's transitive support for B.
Validate the authored Solution-to-Solution support graph for cycles using the
same acyclicity check as other directed dependency relations.

A Spec Policy applies top-down to matching Spec Atoms in its own Component
and the full descendant tree. Its `affects` filter can use any criteria,
including Lens, Tier, Template, a Concern Path subtree, and the logical
Component name. `component.name` refers to the Component containing the Atom.
For a child’s Purpose and Manifest, that is the parent Component’s name.
A parent can use a Spec Policy to constrain `io_allowance` in the child
Component Manifests it contains.
SPEC covers the result and its Realization. PMETA covers the local meta-model
and internal Project Workflows. Only PMETA Workflows can govern Ticket Atoms.

```yaml
affects:
  component.name: ADAPTER_*
```

An Atom can be affected by several Policies and several Solutions. Actors
resolve conflicting claims the same way they resolve other Specification
conflicts. A QA Policy can select Test Case Atoms by Template. A QA Standard
applies directly to the relevant test code throughout its Component tree.

### Source notes

Gemini transcript lines 9878–9886, 10298–10300, 20812–20814, 21157,
22467–22471, 22793–22908, and 23282–23292. Lens names follow the later direct discussion.
Second brainstorm, lines 699–852, 897, 949, 1024, 1073, 1117, and 1214–1318.
The strict meaning of viewpoint follows [ISO/IEC/IEEE 42010:2022](https://www.iso.org/standard/74393.html)
and [The Open Group’s ArchiMate guidance](https://archimate-community.pages.opengroup.org/workgroups/archimate-101/).
Third brainstorm, lines 2015, 2357, 2569–2970, 3112, and 3211.
Fourth brainstorm, lines 223, 294, 507, 557, 610–614, 668, and 723.
