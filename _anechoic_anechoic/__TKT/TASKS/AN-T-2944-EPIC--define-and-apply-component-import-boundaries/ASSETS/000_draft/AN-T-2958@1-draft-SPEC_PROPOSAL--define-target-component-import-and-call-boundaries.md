---
atom_family: TKT
atom_id: AN-T-2958
structure:
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

C27 has exactly one cross-Component code dependency. It imports and
calls the single public Test Suite entry point. The Test Suite owns
discovery, fixtures, and execution of individual tests. It returns a
pass/fail outcome and a report to C27.

C27 consumes artifact and build inputs as data. Define the owner of
installation and startup when mapping release responsibilities.

### Import policy and acceptance

- Record approved provider entries in `boundaries.code_access`. Use
  `__family_pub` for eligible parent and sibling Packages and `__pub`
  for consumers outside the Package family. Keep unmarked Modules
  Package-local.
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
- Verify that C27 imports and calls only the approved Test Suite entry
  point across Component code boundaries.
- Map the target roles to current Component IDs and bind exact Contract
  revisions to their realization Packages. First resolve forbidden
  cross-Component imports from the highest Layer down. Begin the
  target refactor after that pass.

## References

AN-T-2944 and AN-S-3179@1.

Manifest Runtime Contracts AN-S-3089@1, AN-S-3090@1, AN-S-3091@1, and AN-S-3186@1.
