---
atom_family: TKT
atom_id: AN-T-4091
container:
  atom: AN-T-4087
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-28T08:08:02+00:00'
---
## Summary

Verify fresh installation and upgrade

## Work

Use AN-T-2072 and the sealed candidate. Replay INSTALL.md on a fresh
Project and upgrade a disposable Project from a supported prior
version. Use the documented upgrade path for the prior settings.

## Acceptance

Record source SHA, old and new image IDs, readiness, MCP initialization
and a real query. Verify the image actually changes on upgrade.
Preserve Project records, settings, port, data, and image retention.

Verify the documented rerun behavior and the pinned-image reuse
warning. Correct the Setup prerequisite list and the obsolete
repo-root project.toml reference in the Release guide.

## Test isolation

Qualify the release on OrbStack. Keep the disposable Project root,
port, data, and Framework database separate from the running service.
Setup shares one writable Framework database volume per daemon.

## Prior native settings

The available 0.4.4.76 image records source `cf44b0a440e9ef3145022b983ebc9816aeb6056c`.
Its Setup guide uses the host `anechoic/runtime.toml` settings path.
The current guide now explains how to carry those settings forward.
Three focused settings tests passed, including the old path replay.
Native 0.4.4.76 Setup reached Ready on a disposable OrbStack Project.
MCP ran SQL and created and read back RUP-T-1@1-draft. The baseline
records the exact image, Project files, disk database, and saved port.
Setup changes the Compose identity when it adopts mounted settings.
The guide now requires stopping the prior container for this migration.
The candidate install and upgrade checks remain open.

The candidate selected port 55801, disk Workbench, DuckDB Journal,
and INFO logging from the saved legacy file. Both image build paths
selected the same 1,422 inputs and fingerprint on `cd3c911537`.
Verify the immutable image IDs after launch.

Setup also selected the documented disk Workbench and file Journal
defaults for the empty disposable Project. Installation is pending.
