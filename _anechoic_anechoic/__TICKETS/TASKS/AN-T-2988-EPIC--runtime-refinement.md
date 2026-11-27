---
atom_family: TKT
atom_id: AN-T-2988
container:
  component: C00
priority: 2
context:
  template: task
  label: Epic
state:
  status: in_queue
  version: 1
  updated_at: "2026-11-22T18:26:50.927221+00:00"
---
## Summary

Runtime Refinement

## Objective

Give the delivered framework, each Project, and the host runtime clear storage boundaries.

## Scope

- Framework database. Keep a shared DuckDB file on a named Docker volume mounted at `/var/lib/anechoic` inside the container. Use the same mount on every supported host. Build or refresh `framework.duckdb` from the delivered Active Meta-Ontology and Meta-Methodology Atoms when their content changes. The Markdown Atoms remain the source of truth.
- Project database. Keep one host-backed DuckDB file per Project at `.anechoic_runtime/db/project.duckdb`. Store Project projections and the Journal there when the Project Manifest selects DuckDB Journal storage. Preserve existing databases and Journal records during migration and restart.
- Host runtime settings. Reuse `$XDG_CONFIG_HOME/anechoic/runtime.toml`, with `~/.config/anechoic/runtime.toml` as the fallback and `--host-settings` for an explicit path. Keep host listener, served Projects, and runtime limits there. Project choices stay in that Project's Manifest.
- Incremental Startup. Establish watcher coverage before capture. Reuse a compatible checkpoint and apply offline source changes. Admit the Current and Draft base and replay queued live changes through the completed observation before readiness. Scan Archive filenames for maximum versions and load Archive content in the background. Apply queued Archive changes after the load.
- Project Manifest hot reload. Watch the live Manifest. Validate a replacement binding and reload the affected Project in the running container. Run one Manifest Builder per selected Project at a time. Within the pinned binding, coalesce pending input changes into one follow-up build. Publish the exact Model and Structure together.

## Done when

Verify on macOS with Docker Desktop and on Linux with Docker Engine. On Windows, run Setup in WSL 2 with Docker Desktop integration and Linux containers. Verify Projects on the Windows drive and in the WSL filesystem.

On each platform, verify that Setup loads the host settings and mounts the Project directory. Verify that a replacement container and a host reboot preserve the framework database and reopen the same Project databases. Two Projects can query the shared framework database and retain separate Project data. The migration preserves saved state and Journal records.

Verify an unchanged restart and offline additions, edits, moves, and deletions.
Verify full reload when the projection database or a valid checkpoint is
missing. For compiler input changes, verify that unchanged projected columns
preserve the database and refresh only affected data. Verify a rebuild when
column names or types change. Verify that a Graph-only change reuses Model
and Structure. Record time to live readiness and Archive completion separately.
Verify that lifecycle allocation uses the filename scan and that
operations that need exact Archive content wait for the background load.

Edit watched inputs during capture. Verify that Studio admits the base,
replays the queued changes, and then reports readiness. Verify that lost
coverage reconciles the affected inputs before Studio reports them current.

At live Project entry points, verify that a formatting-only Manifest
edit preserves compatible artifacts and that a semantic edit applies
the new settings. Verify that an invalid edit reports the error and
blocks affected writes.

Edit Manifest inputs repeatedly during a build for one pinned binding.
Verify that one follow-up uses the newest observed inputs and that
affected writes stay blocked until Kernel admits their Model and
Structure together.

## Memory and background refresh

1. AN-T-4012 profiles Orchestrator memory first.
2. AN-T-4016 releases superseded polling snapshots promptly.
3. AN-T-4017 fixes Archive admission without a full native rebuild.
4. AN-T-4013 queues Archive events for the normal flow after the background load and skips stale inputs.
5. AN-T-4018 measures Archive admission memory and bounds the handoff if needed.
6. AN-T-4019 reduces time to foreground readiness on cold and incremental startup.
7. AN-T-4022 starts automatic Realization Graph work after Archive settles.
8. AN-T-4014 schedules Realization Graph refresh and exposes the API and MCP request.
9. AN-T-4015 measures Graph admission and changes the handoff if the measured cost warrants it.

## Progress

- Watcher recovery checks the persisted carrier inventory and applies its delta after a complete poll. A live outage test recovered an edit, addition, deletion, and Archive edit without a second rebuild. Archive replacement precedes cross-scope reconciliation.
- A disk restart after a Component Manifest edit refreshed Model and Structure and retained Atom and Archive rows. A projected column mismatch caused a rebuild. The refresh covers the same Project binding. Changes to stored relation semantics still require reconciliation.
- On macOS, two Projects queried 1,312 delivered Framework Atoms and their own migrated Journals through MCP. A replacement container reopened all three databases.
- The release package excludes the selected Project Manifest and root Goal. The canary copies them from the selected Project. The package builds, and the focused tests and isolated static suite pass.
- The full Project cold canary still exits when Workbench cannot start the Kernel within its existing startup limit. The frozen candidate's image gate also failed shared-runtime readiness and the browser storage fallback test.
- Beta keeps its separate Workbench projection database. Its Journal uses the new Project database path.
- Host reboot, native Linux, and both Windows project locations under WSL 2 still need verification.
