---
identity:
  atom_id: CA-A-1461
  ref_id: CA-A-1461@1-draft
context:
  container:
    scope_unit: CA-SU-00
  role: analysis_and_advisory
  form: Spec Proposal
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC
  tier: 3
state:
  status: draft
  version: 1
  updated_at: '2026-11-16T21:30:26.499935+00:00'
destination:
  file:
    name: CA-A-1461@1-draft-SPEC_PROPOSAL--name-the-project-anechoic-and-define-its-component-structure.md
    path: .anechoic_anechoic/02_analysis_and_advisory/000_draft
---
## Summary

Name the project Anechoic and define its component structure

## Proposal

Use **Anechoic Iceberg on Rails** as the full name, **Anechoic** as the short name, and
**AN** as the proposed prefix for new project identifiers. Keep
`anechoic-graph-sdd-framework` as the working repository slug.
Use Workbench for operators and MCP for agents. Maintainer and CI shell scripts
cover build, release, and recovery.

### Framework Components

Meta-ontology, Meta-methodology, Engine Studio, Framework Delivery, and
Operator Documentation are direct children of the Anechoic Project
Component. Retire the legacy Community Extensions, Core Extensions, and
Field Components from the target tree. Migrate their records under the
Project and preserve each revision history.

Retain C9 as Meta-ontology. Retire C10 through C13 as Components and
migrate their Atoms into C9 with their histories. Meta-methodology starts
as a separate Project child.

Retain histories from Workflow Orchestrator and Graph UI under Apps
(C20), Discover Tools under Tools (C16), and the old Workbench Codex
branch under Workbench (C43). Preserve the original paths in the
migration receipt.

| Component | Purpose |
|---|---|
| Meta-ontology (Ontology Pitchfork) | Defines the model Projects use to express their concepts and relationships. |
| Meta-methodology (Methodology Metronome) | Defines the framework’s ways of working using the Meta-ontology. |
| Engine Studio | Groups the runtime and its interfaces. |

### Engine Studio

| Component | Purpose |
|---|---|
| Kernel Mixer | Runs asynchronous engine work. |
| Backend Deck | Provides the shared synchronous read/write API. |
| IWE Console | Provides the operator-facing workspace. |
| MCP Patchbay | Exposes runtime tools through MCP. |

The rename Epic places Kernel Mixer, Backend Deck, IWE Console, and MCP
Patchbay under Engine Studio. The mechanical migration first keeps C14 and
its existing descendant IDs and parent links.
Chamber remains a candidate for a future orchestrator. If a separate harness is added,
revisit the transcript’s **Stagebox** for MCP tooling and **Patchbay** for the harness.

### Project structure

The Project directory is the root of **Realization** (`real`). Component
Packages, product code, tests, CI/CD, enablement, and trace sidecars live
under this root. Use **Implementation** for product code in the narrow sense.

A Project has four top-level logical trees.

| Tree | Root relative to the Project | Contents |
|---|---|---|
| REAL | Project root | Code, tests, and deployment assets. |
| SPEC | `.anechoic_<project_name>/` | Product and system Specification, the model, Manifests, and Purposes. |
| PMETA | `.anechoic_<project_name>/_PMETA/` | Internal Project Workflows and local meta-model extensions. |
| TKT | `.anechoic_<project_name>/__TKT/` | Individual cases of Project work. |

For Anechoic, the records directory is `.anechoic_anechoic/`. REAL covers
the Project files outside the records directory. SPEC covers the records
directory outside the reserved `_PMETA/` and `__TKT/` subdirectories.
In a monorepo, resolve these paths from each selected Project root.

`docs/` describes the product as built. The **Project Goal** is the root
Component’s **Purpose** and guides the Project. The **Project Manifest**
declares the Project, including its name, ID prefix, and other Project
configuration. The native tree uses that Manifest as its sole Project
configuration source. Both are Tier −1 and live in SPEC.

**Axioms** are truths the Project accepts as premises. They are Tier 1 general
`SPEC`. **Applicable Principles** guide Project choices and are Tier 2 general
`SPEC`. They stand on their own without requiring Contracts. Tiers are local
to each Component. Product Definition remains optional when business intent
needs its own section.

### Source notes

Gemini transcript lines 7511, 11078, 11188–11355, 21425, and 23470–23472.
The MCP Patchbay name follows the later direct discussion.
Second brainstorm, lines 595, 645, 949, and 1073. The maintainer CLI choice
follows the later direct discussion.
Third brainstorm, lines 2–144, 672, 2015, and 2251–2445.
Fourth brainstorm, lines 802–848.
