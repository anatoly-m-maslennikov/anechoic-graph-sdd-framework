---
atom_family: TKT
atom_id: AN-T-2710
container:
  atom: AN-T-2711
priority: 2
context:
  template: task
  label: Subtask
state:
  status: done
  version: 6
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Verify read-only interrupted status without recovery or replay

## Objective

Verify the public read-only status and recovery boundary after an accepted
terminal/interrupted_pending result. Preserve the canonical graph result,
make the explicit recovery requirement observable, and prove that status
inspection does not mutate the Run or replay completed Actions.

## Details

One Task per file; at most 15 minutes of own work. Split before expanding.
Review and update dependent Tasks after the observed result and before
execution. Use the current PROGRAMMATIC M/E/D guidance, the locked uv
environment and the bounded source-bound fixture. Preserve exact prior
receipts, source pins, Project identity, partial-result visibility and
business-only Journal semantics. Record the read-only storage/API boundary
owned by the checkpoint worker; root owns observation integration. Create a
Concern for a new blocker. No production MCP traffic, Docker action,
full-suite run, release, deployment, uncertain replay or Git publication.

## Definition of Done

Against frozen nonproduction inputs, assert the exact canonical terminal and
interrupted_pending fields, the corresponding graph_result, the final public
status and its recovery message. Confirm that read-only status and recovery
inspection preserve the existing Run root, do not replay completed Actions,
and do not invent a successful completion. Keep current Project binding,
runtime admission and handoff as separate gates.

### Accepted completion evidence — 22 October 2026

The bounded read-only status/recovery verification passed: 64/64 focused integrated-action checks, six direct observation guards and seven checkpoint checks; strict SDK journey 4/4 in 30.110s with exact terminal/interrupted_pending state, final public status and verified graph-result bytes; final Docker-free stdio smoke with 23 tools; Ruff and mypy passed. The status path preserves the canonical interrupted state without granting recovery permission, replaying completed Actions or inventing completion. No production, release or deployment claim is made.
