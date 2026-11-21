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

Use two server-side runtime Components, a stateless API Backend and a
stateful Kernel. Treat the web frontend, MCP, and Codex Hook as entry
points with their own boundaries. Declare code imports and protocol
requests separately.

### Entry points

- The web frontend and MCP import zero other Project Components. They
  use the API as their only interface to the server runtime.
- The Codex Hook imports zero other Project Components and makes zero
  outbound calls. The host supplies its input and consumes its output.
- The API Contract defines Project identity, request and response shapes,
  errors, and the lifecycle of asynchronous operations.

### API Backend, Tools, and Adapters

The API Backend owns request handling, Tool dispatch, and runtime
composition. It can import the Kernel's public API. The Backend supplies
the Adapter with the specific Kernel operations that the selected Tool
needs.

Each Tool may import Adapters as its only cross-Component code
dependency. An Adapter imports zero other Project Components. When an
Adapter needs a Kernel operation, it receives that operation from the
Backend as an explicit dependency.

### Kernel

The Kernel owns authoritative shared and durable state for each Project.
Kernel Core owns DB access, transactions, and state invariants. Kernel+
owns source watching, graph building, and related projections. Kernel+
publishes state through Kernel Core.

The Kernel imports zero code from the API Backend, Tools, or entry
points. The Backend accesses Kernel services through the public Kernel
API.

### Manifest Runtime

Kernel+ owns the Manifest Builder, Model Host, and Structure Host.
The watcher triggers the Manifest Builder. Each build runs in a
short-lived separate worker process. The builder compiles the admitted
Model and validates the Structure against it.

The builder produces versioned Model and Structure artifacts on disk.
Each Structure snapshot records its Model fingerprint. Kernel+ publishes
the accepted pair atomically. Each operation holds one generation. A
failed build leaves the last accepted generation available.

The hosts expose accepted artifacts through read-only interfaces and
import zero builder code. The Model Host exposes generated modules or
a schema, and consumers load any required Python types locally. Keep
the reader outside the builder Package.

Start with a disk-backed JSON snapshot for Structure. Use an indexed
snapshot with record-level access if measurements show that whole-file
parsing uses too much memory. Start with thin reader entry points. Use
a long-lived host process when it needs to serve requests or manage a
shared cache.

### Workers

Put Tool execution workers in the API Backend by default. Put source
watching and graph workers in Kernel+. The Kernel owns durable job
status and results. A separate worker process can remain inside its
owning Component. Introduce a Workers Component if it needs a separate
Contract and owner.

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
- Verify that the Backend uses the public Kernel API, each Tool imports
  only Adapters across Components, and Adapters import zero other
  Project Components.
- Verify that Kernel Core alone accesses the DB, Kernel+ uses Core for
  state writes, and the Kernel imports zero Backend, Tool, or UI code.
- Verify that builds run in their own worker process and that both
  hosts read the accepted generation without importing builder code.
  Reject a mismatched Model and Structure pair. Verify that a failed
  build leaves the last accepted pair readable.
- Verify that C27 imports and calls only the approved Test Suite entry
  point across Component code boundaries.
- Map the target roles to current Component IDs and bind exact Contract
  revisions to their realization Packages. Finish Tasks 1–4 in
  AN-T-2944 before changing caller imports.

## References

AN-T-2944 and AN-S-3179@1.

Manifest Runtime Contracts AN-S-3089@1, AN-S-3090@1, AN-S-3091@1, and AN-S-3186@1.
