---
atom_family: TKT
atom_id: AN-T-2958
container:
  atom: AN-T-2944
priority: 2
context:
  template: Spec Proposal
state:
  status: draft
  version: 1
  updated_at: '2026-11-21T18:15:25.910956+00:00'
---
## Summary

Define target Component import and call boundaries

## Proposal

Use three server-side runtime Components, the API Backend, Workers,
and Kernel. Treat the web frontend, MCP, and Codex Hook as entry points
with their own boundaries. Declare code imports and protocol requests
separately.

### Entry points

- The web frontend and MCP import zero other Project Components. They
  use the API as their only interface to the server runtime.
- The Codex Hook imports zero other Project Components and makes zero
  outbound calls. The host supplies its input and consumes its output.
- The API Contract defines Project identity, request and response shapes,
  errors, and the lifecycle of asynchronous operations.

### API Backend

The API Backend serves Web and MCP. It calls the Workers Jobs API to
submit jobs and read status and results. It calls the Kernel's database
API directly for database requests, including interactive Run Query.
The Kernel executes SQL. The Backend handles the request and response.

Use a worker for an explicit asynchronous job, such as a long export,
when the caller needs job status or a result delivered later.

### Workers, Tools, and Adapters

The Workers Component owns the Jobs API, file watcher, and supervisor.
The supervisor turns file events and submitted requests into one-shot
or batch jobs. It coordinates worker processes and owns the meaning of
job status. Store durable job records and results through the Kernel.

Tool operations, graph builds, and Manifest Builder runs execute in
worker processes. Each Tool imports Adapters as its only cross-Component
code dependency. Adapters import zero other Project Components.
Worker process composition supplies any authorized Kernel operations to
the Adapter for the selected job.

### Kernel

The Kernel is the database server for each Project. It owns DB access,
transactions, and database invariants. It serves the Backend and
Workers through its public database API. The Model Host and Structure
Host are read-only interfaces in this same Kernel process.

### Manifest Runtime

The Workers supervisor starts the Manifest Builder in a short-lived
separate process. The builder compiles the admitted Model and validates
the Structure against it. It emits a versioned Model schema and
Structure snapshot. Start with JSON for both artifacts.

Record the Model fingerprint in each Structure snapshot. The supervisor
activates the accepted pair atomically. Each read operation holds one
compatible generation. A failed build leaves the last accepted pair
available.

The Kernel's Model and Structure Hosts expose the accepted artifacts
with zero Builder imports. Consumers that need executable Python types
load them locally. Use an indexed Structure snapshot if measurements
show that whole-file JSON parsing uses too much memory.

### Framework Delivery (C27)

Split Release into two child Components within Layer 5. Local Release is
the lower layer. Public Release is the upper layer and may use declared
Local Release exports and CLI interfaces. Local Release may neither
import from nor call Public Release. Declare this direction in the child
Component Manifests.

Release has zero code imports from Components outside its subtree.
Local Release calls the single public Test Suite entry point as its
sole external Component interface. The Test Suite owns
discovery, fixtures, and execution of individual tests. It returns a
pass/fail outcome and a report to C27.

Local Release owns release orchestration, installation, and startup. It uses the
standard library, Git, Docker, and artifact and build inputs as data.
It commits pending nonignored changes under existing protections, then
bumps and commits the candidate Version.

Local Release calls the Test Suite once for unit tests and linters. After
that gate passes, it prepares the retained governed Framework, runtime, and Skill
package and builds one immutable candidate image. It calls the same
Test Suite entry in end-to-end mode on that exact image, then runs a
disposable canary before production.

After both pass, Local Release installs the verified files and starts the
exact image
on the Project-owned Manifest `project_mcp.http_port`, checks readiness,
and applies the production tag to that same image ID. It retains the
verified previous image when available. Failures report observed effects
without automatic replay.

Public Release prepares the detailed PR description for a selected
Local Release and derives a brief Version History entry from it. The
entry summarizes the main user-facing changes. These are the two
outputs of Public Release.

Pin the PR base (`main`) and head (`amm/dev`) commits for both evidence
sources:

1. Read completed Task and Epic files from the Git repository. Use
   records that describe changes included in the selected release as
   the primary evidence.
2. Have Luna review the Git diff for the same PR comparison. Add
   relevant changes that the completed Tasks and Epics do not cover.
   Combine overlapping evidence in one PR entry.

Read the Task and Epic files and the diff directly with Git. This work
requires no ANECHOIC runtime, MCP, or Workbench.

### Code Access

- Under `boundaries.code.exports`, entries without a declaration or
  marker stay private to the owning Package. An export with omitted
  visibility defaults to shared for the parent and siblings. Public
  exports admit any caller at the export boundary.
- Mark shared entries with `__shared` and public entries with `__pub`.
  An explicit export can grant access to named callers.
- Under `boundaries.code.imports`, direct children, siblings, and
  public entries are eligible by default. A list adds named dependencies.
  Use `only` for a closed list. An empty `only` list allows zero
  cross-Package imports.
- Every cross-Package import must pass caller and provider rules.
  Within an ordered sibling group, dependencies point from higher
  layer numbers to lower ones. An allowlist cannot bypass layer order.
- Preserve existing restricted imports and exports when migrating their
  declarations. Rename `__family_pub` to `__shared` and migrate the
  associated imports and visibility declarations together.

### Runtime I/O

Use `boundaries.io.client` to name the provider Component and interface.
Under `boundaries.io.server`, the provider declares `transport: cli`,
the runner, path, and any required command. For
example, Local Release calls the named Test Suite CLI in Project Tools.
MCP over stdio uses the MCP protocol and a separate interface.

### Acceptance

- Verify zero cross-Component imports from the web frontend, MCP, and
  Codex Hook. Verify that web and MCP use the API and that the Hook
  completes with host input and output only.
- Verify that the Backend reads job state through the Workers Jobs API
  and executes interactive Run Query through the Kernel database API.
- Verify that each Tool imports only Adapters across Components and that
  Adapters import zero other Project Components.
- Verify that the Kernel owns persistent state and serves its Model and
  Structure interfaces in one process. Verify that the Manifest Builder
  runs in a separate worker and that the hosts import zero Builder code.
- Reject a mismatched Model and Structure pair. Verify that a failed
  build leaves the last accepted pair readable.
- Verify zero code imports from Components outside the Release subtree.
  Verify that the approved Test Suite entry is the only external
  Component interface called by Local Release.
- Verify that Public Release reads completed Tasks and Epics directly
  from Git and uses Luna to find omissions in the same PR diff.
- Verify that the detailed PR description and brief Version History
  entry describe the same Local Release.
- Verify that the two Release Components allow Public Release to use
  declared Local Release interfaces. Reject Local Release imports and
  calls into Public Release.
- Map the target roles to current Component IDs and bind exact Contract
  revisions to their realization Packages. First resolve forbidden
  cross-Component imports from the highest Layer down. Begin the
  target refactor after that pass.

## References

AN-T-2944 and AN-S-3179@1.

Manifest Runtime Contracts AN-S-3089@1, AN-S-3090@1, AN-S-3091@1, and AN-S-3186@1.
