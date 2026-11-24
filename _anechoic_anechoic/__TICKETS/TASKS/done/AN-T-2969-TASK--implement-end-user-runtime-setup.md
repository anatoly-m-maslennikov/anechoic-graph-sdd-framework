---
atom_family: TKT
atom_id: AN-T-2969
container:
  component: C00
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: "2026-11-21T23:20:08.050938+00:00"
---
## Summary

Implement end-user Runtime Setup

## Work

Provide a host installer for one Git repository or a folder of repositories. Build the runtime image through Release, start the shared Docker runtime on the configured port, and verify MCP readiness.

Store the mount, port, and default Workbench and Journal storage in Runtime Setup settings. Initialize a new Project only on explicit request. Document the installation steps for agents and humans in the root `INSTALL.md`.

Support optional `--agent codex` installation. Register the shared MCP endpoint and a user-level hook that sends the nearest Git worktree root, including from nested working directories.

## Completion evidence

Implemented by commit `70acf2c214` under Runtime Setup (C65), with Manifest AN-S-3296 and Contract AN-S-3297.

Verified Docker installation in both modes. In folder mode, one installed hook routed from nested directories to two separate repositories and the runtime rejected a repository outside the mount. Verified Codex MCP registration in an isolated user configuration. Codex asks the user to trust the hook.

Passed 137 focused tests.