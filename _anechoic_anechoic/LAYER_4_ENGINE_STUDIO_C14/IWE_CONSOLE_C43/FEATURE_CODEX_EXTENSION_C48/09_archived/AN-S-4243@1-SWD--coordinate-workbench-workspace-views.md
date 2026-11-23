---
atom_family: SPEC
atom_id: AN-S-4243
container:
  component: C48
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 16:45:35 +0400
---

## Summary

Coordinate Workbench Workspace Views

## Claim

Use the existing native Codex chat as the Workspace boundary. Keep one Workspace per native chat and keep its Views isolated from every other chat and Project.

Implement View operations as small adapters over the existing query executor, pagination, successful-run saving, saved Journal and browser autosave. Keep the caller's order; do not add a magic Workflow or a new scheduler. Return Run metadata first and fetch result rows only when requested.

Keep the query log separate from saved Views. Record only the approved SQL, outcome, error and counts, retain it for seven days, and expire old entries when the log is read. Do not store rows, duplicate schema data or add a cleanup daemon.
