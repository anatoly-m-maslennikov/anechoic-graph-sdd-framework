---
atom_family: TKT
atom_id: AN-T-4044
container:
  atom: AN-T-4039
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: "2026-11-26T22:18:31Z"
---
## Summary

Show Project Structure and its Specs

## Work

Add a Structure view for Components and Component Seeds. Use their
purposes as summaries. Give each entry one-click access to its
Manifest and Solution through the shared Document view.

## Acceptance

Verify the Structure hierarchy, purpose summaries, and one-click
Manifest and Solution links for a Component and a Component Seed.

## Verification

Current DuckDB projects Component Purpose and admitted Component
Seeds. The native owner test verified exact Manifest and Solution
navigation, rejection of stale Solution pins, watcher publication
with Imports disabled, and reuse of a retained database.
All seven Structure browser cases passed.
Kernel Contract AN-S-3047@33 covers the projection.
