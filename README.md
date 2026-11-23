# Anechoic Iceberg on Rails

**The Graph-Driven Development Framework**

## Contents

- [Install](#install)
- [The Goal](#the-goal)
- [What Anechoic is](#what-anechoic-is)
- [Why Anechoic works this way (chains-of-thoughts)](#why-anechoic-works-this-way-chains-of-thoughts)
- [Main framework architecture](#main-framework-architecture)
- [First usable cut](#first-usable-cut)
- [Current boundaries](#current-boundaries)
- [Status](#status)
- [Version History](#version-history)
- [Thanks](#thanks)

## Install

See [INSTALL.md](INSTALL.md) for local setup, including instructions for an AI agent.

## The Goal

If it can be built, Anechoic should help anyone build it if they are willing to invest the time and effort.

In practice, it should make AI-assisted development reliable from the first idea to production without losing meaning, traceability, or learning.

Even a fully AI-generated project should be understandable, controllable and **not slop**.

## What Anechoic is

Anechoic stores project knowledge as small artifacts connected by typed links. Humans and AI use this graph to understand the project, make changes, check consistency, and generate useful views.

## Why Anechoic works this way (chains-of-thoughts)

Prompts/Skills, MCP, Apps and execution Tools form the harness →\
the project's meaning must not depend on them →\
an explicit ontology/base model defines the core: concepts, relations and constraints.

### Ontology (methodology)

The project is made of implemented decisions—yours and AI Agents' →\
But sessions are ephemeral →\
We need a **stable source of truth** →\
It's the specification.

Spec grows →\
we need smaller units →\
no single file structure is optimal for every use case →\
a graph with typed nodes and typed relations.

Each unit should be the smallest meaningful part of the spec →\
one scope + one Claim = one Atom →\
splitting further adds no useful distinction.

Nodes represent different things →\
Atoms state Claims; Entities are the things those Claims describe →\
Subjects link Atoms to Entities through `GOVERNS` and `DEPENDS_ON`.

Different tasks need different views →\
derive them from one authoritative source →\
**load only the context needed without duplicating authority.**

Natural-language phrases can be ambiguous →\
shared vocabulary + Anechoic Controlled English (CCE), a constrained way to write Claims →\
**explicit, checkable Claims.**

The spec is about different things →\
Requirements — required outcomes →\
Methods — how code should be written →\
Evaluations — QA rules and test-case specifications →\
Delivery — where and how to deliver results →\
together, RMED.

Describing an outcome does not prove it was achieved →\
Evaluations define checks →\
actual runs provide evidence.

We need more than spec →\
Concerns, Analysis and Plans for understanding and planning →\
Implementation for code, tests and configuration →\
Operations for repeatable actions and workflows.

Repeatable sequences of actions →\
Operations define Workflows, their steps and control flow.

Implementation, tests and views rely on Claims →\
record the exact source Claim identities and revisions →\
**trace results back to the specification.**

A typical iteration starts with a Concern →\
Analysis →\
Plan →\
RMED →\
Implementation →\
checked outcomes →\
next Concern.

Journals record changes and execution. Not every change needs every stage.

Using the same system for projects and methodology is simpler →\
both use Atoms, content roles and relations →\
the same Tools and Prompts can work with both →\
**the framework is built with the framework.**

The framework must describe itself →\
the [meta-ontology](LAYER_1_META_ONTOLOGY_C9/) uses Atoms to describe Atoms and other framework concepts →\
this creates recursion and needs a starting point →\
bootstrap seeds provided the first definitions; those seeds are now retired.

Different projects need different rules →\
Extensions and local configuration are also sets of Atoms →\
they add only Core-permitted capabilities and configuration, without replacing or weakening Core authority →\
**expand and configure the framework using the same system.**

### Harness (engine)

Ontology is big and complex →\
operating a project with the framework should be simple →\
harness, Tools and Prompts should show this complexity only when needed →\
ontology and engine are the "backend"; Skills and Prompts are the "frontend".

Skills vary a lot →\
different people prefer different Skills →\
the framework harness should support third-party Skills as a **replaceable frontend/interface**.

Repeated model reasoning costs time and tokens →\
every repeatable task that can be done deterministically should run programmatically →\
**Tools save time and tokens.**

Work that cannot be done deterministically →\
LLM reasoning →\
repeatable actions need reusable Prompts/Skills.

Workflows are defined in Operations →\
the harness implements and runs them using Tools and Prompts/Skills.

We cannot put everything into one prompt →\
the built-in entry Skill, [ane](LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_SKILLS/ane/SKILL.md), connects agents to MCP →\
Tools retrieve the needed context and assemble Prompts/Skills →\
MCP delivers them and exposes Tool and Workflow execution.

Wide-context reasoning →\
main session.

Narrow, repeatable work →\
bounded execution contexts and structured results.

Long actions should not block sessions →\
Workflow Orchestrator coordinates the steps in the background →\
durable state, reconnectable runs, approvals and recovery.

Files in folders are clear and inspectable →\
they currently hold authority →\
rescanning can become expensive →\
a derived graph database index supports queries and views. Database authority could be a future migration.

## Main framework architecture

### Core Nodes

- **Scope Unit:** one area of project responsibility, declared in the project structure.
- **Atom:** one Claim in one scope, with a Role. Atoms belong to Scope Units; project-wide goals are the exception.
- **Journal:** records of changes, execution and observed outcomes.
- **Projection:** a derived, non-authoritative view of existing sources.

### Roles and Forms

- **C — Concern:** problems, bugs, questions and opportunities.
- **A — Analysis & Advisory:** analysis reports, rationale and spec proposals.
- **P — Plan:** backlog, tasks, epics and version plans.
- **R — Requirement:** specification of required outcomes.
- **M — Method:** how code should be written.
- **E — Evaluation:** quality assurance policies and test-case specifications.
- **D — Delivery:** target environments, CI/CD and release policies.
- **O — Operations:** actions and workflows with steps to operate the project.

Each Atom Role has **Forms**. Each Form has its own structure, properties, authoring rules and checks. For example, Operations has Workflow, Step, Substep and Action.

Role describes purpose. Form identifies the structure used within that Role.

**I — Implementation** consists of code, tests, configuration and CI/CD pipelines implementing RMED.

- **MECE:** cover the defined scope without overlap.
- **DRY:** keep one source of meaning, not independent copies.

**One coherent source of truth:** Atoms record Claims; actual Implementation shows what is built.

### Scope units

A Scope Unit groups Atoms for one part of the project, such as an app, feature or tool. Inside it, Atoms are organized by Role: Concerns, Plans, Requirements, Methods, and so on.

Current Requirement Atoms with Form `Scope Unit Declaration` define Scope Units,
their parents, and their derived authority/Delivery paths. Folders follow those
Declarations.

**Scope Unit levels** show nesting depth. The Project is level `0`. Each child is one level deeper: `1`, `2`, `3`, and so on.

**Scope Units can be ordered or unordered:**

- **Ordered:** has a `local_order` among ordered Scope Units with the same parent.
- **Unordered:** has no `local_order`. The Project itself is Unordered.

Order does not create dependencies. State dependencies separately. Folder numbers are for navigation; they do not set `local_order`.

### Fractal structure

Scope Units can fold one inside another. P Atoms can split into smaller P Atoms: epics, sub-epics, tasks and subtasks.

**As many layers as needed. The same framework rules at every layer.** The structure must not contain cycles.

### Atom tiers

**Local tiers** show an Atom's authority inside its Scope Unit:

- **Principle:** project principles.
- **Core:** basic definitions and boundaries.
- **General:** reusable rules.
- **Standard:** work and implementation details.

From higher to lower authority:

- Project: Principle, Core, Standard.
- Other Scope Units: Core, General, Standard.

**Global tiers** give Atoms one authority number across the project. The number comes from the scope and Local Tier. Within the scope where a Claim applies, a lower number means higher authority.

Project goals have Global Tier `-1` and no Local Tier. **Tiers are not work priority or folder depth.**

Agents act within delegated authority →\
they can analyze conflicts and propose resolutions →\
only the Operator can resolve conflicts between active Project Principles.

### Ownership and claim scope

- **Internal:** the project defines the meaning.
- **External:** an outside source defines or imposes the meaning. The project records the source and how it applies.
- **Relational:** a Claim targets another Scope Unit, or the Atom is not inside a Scope Unit.

Internal/external say **who defines the meaning**. Relational says **where the Claim applies**.

### Relations

**Direct relations** link artifacts. Examples:

- `child_of`: a parent Requirement.
- `method_for`, `evaluation_for`, `delivery_for`: RMED support for a Requirement.
- `derived_from`: the sources used.

**Subjects** link Atoms to Entities:

- `GOVERNS`: what the Claim governs.
- `DEPENDS_ON`: what the Claim needs but does not govern.

Subjects are links, not nodes.

Scope Units + typed relations + Subjects →\
**fetch the right part of the spec or other Anechoic content mechanically, or almost mechanically.**

### Main projections

There can be a lot of Atoms →\
they can be compiled into one Projection →\
**it is still a derived artifact, not a source of truth** →\
for example: one prompt for how to write code, built from all M Atoms that apply to the Scope Unit.

- **Atom Subjects Graph:** Atoms linked to Entities through `GOVERNS` and `DEPENDS_ON`.
- **Entities Graph:** Entities linked to other Entities through allowed relations.
- **Terms Graph:** terms and their allowed typed relations.
- **Project Scope Unit Graph and Sources view:** Scope Units, their parents and authority/Delivery paths.
- **Applicable Methodology:** the rules that apply to the selected scope.
- **Requirement Lineage Map:** Requirements traced back to their Principles.

**Different views, one source.** Rebuild Projections from their sources.

The Project Manifest derives the Atom tree from the Project name and `project.root.prefix`. Use `dot` for `.anechoic_<project_name>/` or `underscore` for `_anechoic_<project_name>/`. This Project uses `_anechoic_anechoic/`. Runtime and temporary data use `.anechoic_runtime/` and `.anechoic_tmp/`.

Local Release delivers Active Atoms directly in `LAYER_1_META_ONTOLOGY_C9/`
and `LAYER_2_META_METHODOLOGY_C58/`. The installed Framework uses the same
layer folders in
`_anechoic_anechoic/000_ANECHOIC_framework/`. Project Atoms are authoritative.

L3 DevOps defines the locked uv environments and owns Release. Runtime Images
builds and runs images for Local Release and L5 User Setup. L4 Engine Studio
runs in the Engine environment defined by DevOps.

Store file-based Journals in `_journal/` and general Projections in `_projection/`.

With an explicit Project root, Journal writes and queries use that Project's settings and Journal, not those of a parent or sibling Project. Ambiguous control folders and symlinked settings are rejected.

### Extension and configuration

**The framework is expandable and configurable.** You can add Types, Workflows, Tools and authoring rules. Put reusable additions in Extensions. Settings choose what to use and with which parameters. Framework rules still apply.

## First usable cut

The current implementation keeps Workbench, standalone Subject/Topics view
builders, and host local/public release. The shared MCP exposes Workbench query,
Workspace, View and service tools. Legacy discovery, Atom mutation, selected
execution, workflow queues and reversal interfaces are retired in code.

The standalone Subject renderer supports seven views without the old execution
engine. See [the retained runtime and builders](.anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/03_plan/CA-P-2849-WORK_REPORT--2848.md)
for entry points, shared dependencies and verification limits. This code-first
retirement does not claim that the corresponding methodology Atoms have already
been reconciled or that an installed runtime has been replaced.

The Release uv Project provides three host commands in the `release` environment.

- **Local Release** checkpoints eligible changes and runs static checks and
  required unit tests before the build. The image suite runs end-to-end and
  canary checks on the exact candidate before Local Release installs the package
  and project-local `ane` and starts and verifies production MCP.
- **Public Release** reads completed Task and Epic evidence at pinned Git commits.
  A second run with the reviewed JSON changes returns drafts for the pull request
  description and Version History entry. The Operator handles publication.
- **Build image** returns the immutable image ID for the checked-out source without
  deploying it or changing the Version.

Use an Operator command to start a release. After production verification,
Local Release keeps the current image and two previous Project images. It removes
only eligible unused images.

Local release skips an empty initial commit; commit failure or remaining changes
stop it before tests, builds or Docker work. Existing environment-file exclusions
remain; excluded nonignored changes must be resolved before release.

The installed Project package is in `.anechoic_runtime/simple_local_release/package`.
Configuration and existing Project records remain outside the replacement
boundary. Engine Studio uses `dev` for QA and `prod` in the runtime image from the
same uv lock. Setup has its own lock and `setup` environment.

Use the locked host commands in [Project release tools](LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/README.md),
with an Operator-selected run ID. The host commands use Git and Docker
independently of MCP. Regular
Project MCP runs in Docker on localhost without a password; the
[launcher documentation](LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/README.md)
describes Project selection and endpoint startup.

Local numbering adds or increments the fourth component (`0.4.2.1` →
`0.4.2.2`). Public numbering increments the third and removes the fourth
(`0.4.2.2` → `0.4.3`). Installed Local and published repository versions are
separate milestones.

The `0.4.2.2` Local run completed on 12 October 2026: all 16 intended tests passed,
delivered Methodology/runtime/Skill files matched their installed copies, and
actual Docker MCP initialization succeeded. This is not a claim that every
historical test or deferred capability passes. The entity-model candidate and
its research remain non-authoritative; full migration is not claimed complete.

### Retained legacy records

Git commit `01346521713cc5647210ee94ab79a9bd4e539360` contains the original
tracked records under `archives/.anechoic_legacy/`,
`archives/.anechoic_archive/`, and `archives/.anechoic_legacy_archive/`.
Read a record from that commit with `git show <commit>:<path>`.
The [native alias map](_anechoic_anechoic/_migration/native-aliases.json)
records the exact native references for migrated records.

The import-graph proposal `CA-A-1467@1-draft` is available as
[`AN-T-2928@1-draft`](_anechoic_anechoic/__TICKETS/ASSETS/01_draft/AN-T-2928@1-draft-SPEC_PROPOSAL--derive-a-module-and-package-import-graph-from-project-source.md).

Use native sources for runtime, QA, and Local Release. Store historical test
inputs under `assets/` in their Test Packages. QA and Local Release must run in
a checkout without legacy archives.

## Current boundaries

- More than one person can use Anechoic on a project, but the framework does not yet provide native support for team workflows.
- Anechoic is not only local-first; it is currently local-only.

## Status

The current framework version is declared in [version.toml](version.toml). The framework foundation is under active development; this is not yet a complete production toolchain.

Anechoic is source-available. See the [license terms](LICENSE) and the
[plain-language summary](LICENSE.TLDR.md).

## Version History

See [Version History](VERSION_HISTORY.md) for project origins and version milestones.

## Thanks

- **[Andrej Karpathy](https://en.wikipedia.org/wiki/Andrej_Karpathy)**, for his fresh ideas—especially about graphs. His [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) says it vividly: “Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase.” His [Software 3.0 talk](https://www.youtube.com/watch?v=XdbpCM4yGyE) develops the graph perspective further.
- **[Daniel Kravtsov](https://improvado.io/blog-authors/daniel-kravtsov)**, CEO and co-founder of [Improvado](https://improvado.io/company/about), for giving me the challenge of building a knowledge graph for my team. It showed me what graphs can achieve in practice. At Improvado, I also tried for the first time to build an internal product both with AI and by AI.
- **[Anatoly Levenchuk](https://t.me/ailev_blog)**, creator of the [First Principles Framework](https://github.com/ailev/FPF). I could never have built this project without FPF. I also maintain an [LLM-friendly FPF knowledge-graph toolkit](https://github.com/anatoly-m-maslennikov/levenchuk-fpf-knowledge-graph-toolkit).

<!-- latest-public-release -->
Latest public release: **0.4.4**. See [Version History](VERSION_HISTORY.md).
