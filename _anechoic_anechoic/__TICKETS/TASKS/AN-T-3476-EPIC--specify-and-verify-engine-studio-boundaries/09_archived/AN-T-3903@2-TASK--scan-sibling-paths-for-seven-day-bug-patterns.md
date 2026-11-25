---
atom_family: TKT
atom_id: AN-T-3903
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 2
  updated_at: '2026-11-24T11:42:32.383070+00:00'
---
## Summary

Scan sibling paths for seven-day bug patterns

## Work

Use the confirmed fixes and independently stated invariants from AN-T-3901 and AN-T-3902 to identify relevant current sibling paths. Inspect those paths for the same defect patterns. Record the scope examined, method, source evidence, and limits.

Record each confirmed defect with a reproducible example and affected path. Distinguish suspected defects, unsupported checks, and paths not examined. Link findings to follow-up work where needed.

## Acceptance

The scan records the paths and patterns examined, evidence for confirmed defects, and explicit unsupported, uncertain, and unexamined cases. It does not claim complete coverage without evidence.

## Confirmed current findings

- Native Ticket status update: a scratch runtime transition of a persisted TKT from `backlog` to `in_queue` retained Version 1 and rewrote `updated_at`. `LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_LIFECYCLE/native_update_selection.py`, `_status_bytes`, explicitly sets both fields; `native_update.py` calls it. Reproduce with a persisted Version 1 backlog Ticket in a scratch Project, transition it to in_queue, and compare the persisted headers before and after. The exact timestamp value and scratch artifact are not retained here.

- C71 native delta: when the base has no `main.int_lifecycle_lenses` table, a submitted delta with an Atom and its Lens returns HTTP 200 and admits the Atom but drops the Lens. Reproduce in a checked scratch workspace from a base without that table, submit an otherwise valid native delta containing `lifecycle_lenses`, and query both the Atom and Lens state. `LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_beta_C67/DATABASE_SERVER_beta_C71/native_delta.py`, `_write_lenses`, writes only when the table already exists. Preserve the request and query output in follow-up evidence.

- C43 bridge readiness: with `bridge.ready` false, GET `/health` returns HTTP 503 with `{"ready":true}`. `LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_CODEX/bridge_server.py`, `do_GET`, selects the status from readiness but writes a constant true body. The defect was present since introduction; a correction was tested only in scratch. Reproduce by serving the handler with a bridge whose `ready` is false and requesting `/health`. The production source remains unchanged.

These are partial scan findings. Exact retained commands and output, remaining sibling coverage, and unsupported cases require follow-up. Keep this Task in queue.
