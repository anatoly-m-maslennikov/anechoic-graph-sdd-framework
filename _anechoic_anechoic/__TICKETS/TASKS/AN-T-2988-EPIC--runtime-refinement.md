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
  status: "in_queue"
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

## Done when

Verify on macOS with Docker Desktop and on Linux with Docker Engine. On Windows, run Setup in WSL 2 with Docker Desktop integration and Linux containers. Verify Projects on the Windows drive and in the WSL filesystem.

On each platform, verify that Setup loads the host settings and mounts the Project directory. Verify that a replacement container and a host reboot preserve the framework database and reopen the same Project databases. Two Projects can query the shared framework database and retain separate Project data. The migration preserves saved state and Journal records.

## Progress

- On macOS, two Projects queried 1,312 delivered Framework Atoms and their own migrated Journals through MCP. A replacement container reopened all three databases.
- The release package excludes the selected Project Manifest and root Goal. The canary copies them from the selected Project. The package builds, and the focused tests and isolated static suite pass.
- The full Project cold canary still exits when Workbench cannot start the Kernel within its existing startup limit. The frozen candidate's image gate also failed shared-runtime readiness and the browser storage fallback test.
- Beta keeps its separate Workbench projection database. Its Journal uses the new Project database path.
- Host reboot, native Linux, and both Windows project locations under WSL 2 still need verification.
