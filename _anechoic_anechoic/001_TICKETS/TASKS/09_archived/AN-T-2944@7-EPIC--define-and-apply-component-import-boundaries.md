---
atom_family: TKT
atom_id: AN-T-2944
container:
  component: C00
priority: 2
context:
  template: task
  label: Epic
state:
  status: archived
  version: 7
  updated_at: "2026-11-21T23:25:36.573750+00:00"
---

## Summary

Define and apply Component import boundaries

## Status

Paused by the Operator. Keep this Epic and its child Tasks on hold until the
Operator explicitly resumes the work.

## Objective

Give each current Component an authored Contract and declare the Code Access,
state, and interfaces that its Realization needs.

## Review checkpoint

- **Framework Delivery (C27).** The current Python scan found zero imports
  outside the Release subtree. The three resolved imports within it dispatch
  to Local Release (C63) and Public Release (C64).
- **Release interfaces.** Local Release calls the single C19 Test Suite CLI for
  unit, end-to-end, and canary gates. Public Release drafts the PR description
  and brief Version History entry from completed Tickets and a Luna review of
  the pinned Git diff. Contracts and exact bindings are in place for C27,
  C63, and C64.
- **Entry Modules and manifests.** The implemented entry Modules use
  `__shared` and `__pub`. AN-T-2945 and AN-T-2946 still need coverage checks
  for each Component and its code-bearing Packages. Use `boundaries.code`
  for Code Access in AN-T-2945.
- **Engine Studio (C14).** The Python scan of the checkout at `0f87987354`
  found 763 denied sites among 768 resolved cross-Component import sites,
  including tests. MCP (C21) accounts for 227 denials. Its largest groups
  reach Tools (C16) and Workbench Backend (C45).
- **Verification limits.** The same scan reported 1,076 unresolved Python
  import sites. It confirmed zero resolved cross-Component imports from the
  Codex Hook (C49). TypeScript requires a separate check.
- **Runtime Setup (C65).** The scan confirmed zero resolved cross-Component
  imports. The installation work is complete in standalone Task AN-T-2969.

## Solution

### Approach

Use three server-side Components. The API Backend serves Web and MCP.
It calls the Workers API for job submission, status, and results. It
calls the Kernel directly for database requests. Interactive Run Query
uses this direct path, so a query can return without starting a worker.

The Kernel is the database server for each Project. Its Model Host and
Structure Host are read-only interfaces in the same process. They expose
one compatible generation of JSON schemas and Structure data.

The Workers supervisor receives file events and starts one-shot or batch
workers. Tool operations, graph builds, and the Manifest Builder run
there. The supervisor owns the job lifecycle and stores durable job
records through the Kernel. A separate Builder process releases its
build memory at exit. Publish a compatible Model and Structure generation
atomically and keep the previous generation available on failure.

The Codex Hook processes host input and returns output to the host.
C27 Framework Delivery exposes the `local` and `public` Release commands.
Local Release calls the Test Suite through its public CLI. Public Release
can use declared Local Release interfaces.

### Processes and calls

Arrows show runtime calls, host input and output, or artifact handoffs.

```mermaid
flowchart LR
    WEB["Web frontend"] -->|API request| API["API Backend"]
    MCP["MCP"] -->|API request| API
    HOST["Codex host"] -->|input| HOOK["Codex Hook"]
    HOOK -->|return output| HOST

    subgraph WORKERS["Workers Component"]
        WATCH["File watcher"] -->|file event| JOBS["Jobs API and supervisor"]
        JOBS -->|start one-shot or batch| TASK["Tool or graph worker"]
        JOBS -->|start build| BUILD["Manifest Builder process"]
        TASK -->|result| JOBS
        BUILD -->|validated artifacts| JOBS
    end

    subgraph KERNEL["Kernel process"]
        DB["Database server"]
        READERS["Read-only Model and Structure Hosts"]
    end

    API -->|submit, check status, fetch result| JOBS
    API -->|Run Query or other DB request| DB
    JOBS -->|store durable job records| DB
    TASK -->|DB access through an Adapter| DB
    JOBS -->|activate compatible generation| ART["Versioned JSON artifacts"]
    ART -->|read| READERS
    LOCAL["C63 Local Release"] -->|run suite via CLI| SUITE["C19 Test Suite"]
```

### Code imports

This is the target import structure. Process calls use public interfaces. Where code imports a client entry
Module, record the exact export in the caller's allowance. Tools import
only Adapters across Components. Adapters import zero other Components.
Web, MCP, and the Hook have zero cross-Component imports. The Kernel's
reader interfaces import zero Builder code.

```mermaid
flowchart LR
    API["API Backend"] -->|database client entry| KERNEL["Kernel API"]
    API -->|Jobs API client entry| JOBS["Workers API"]
    WRUN["Worker process composition"] -->|Tool entry| TOOL["Tool"]
    TOOL -->|only cross-Component import| ADAPTER["Adapter"]
    PUBLIC["C64 Public Release"] -->|allowed declared exports| LOCAL["C63 Local Release"]

    ENTRY["Web, MCP, and Codex Hook<br/>Zero cross-Component imports"]
    READERS["Kernel Model and Structure Hosts<br/>Zero Builder imports"]
```

Record exact providers and entry Modules in Component Manifests. Bind
their Contracts to the owning Packages for the target architecture.
See Spec Proposal `AN-T-2958@1-draft` for detailed rules and acceptance
checks.

## Work

1. Resume AN-T-2949 in Engine Studio (C14). Start with MCP imports from
   Tools and Workbench Backend. Continue in descending Layer order. Verify
   each repair against declared ownership and Code Access. Track unresolved
   imports and keep Package-only findings outside this pass.
2. Complete AN-T-2945. Declare Code Access under `boundaries.code`. Record
   runtime interfaces under `boundaries.io` and owned state under
   `boundaries.state`.
3. Complete AN-T-2946. Check each code-bearing Package separately. Prefer
   one `__shared` entry Module for the parent and siblings. Add `__pub`
   when a public interface is needed. Keep implementation Modules unmarked
   and Package-local.
4. Complete AN-T-2947. Write each Component Contract with a verifiable
   guarantee and implement its interface.
5. Complete AN-T-2948. Bind exact Contract revisions to their Realization
   Packages.
6. Refactor to the target architecture after resolving forbidden
   cross-Component imports. Use Component Seed as the name for a Package
   with its own Spec that may later become a Component.
