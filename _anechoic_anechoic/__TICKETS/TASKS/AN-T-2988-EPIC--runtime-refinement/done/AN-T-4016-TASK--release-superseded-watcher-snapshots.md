---
atom_family: TKT
atom_id: AN-T-4016
container:
  atom: AN-T-2988
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: "2026-11-26T19:10:23Z"
---
## Summary

Release superseded watcher snapshots

## Work

Break the reference cycle between a directory snapshot and its scan
callbacks in Orchestrator. Preserve watcher coverage, change detection,
and scan diagnostics.

## Acceptance

A discarded snapshot becomes collectible without waiting for cyclic
collection. Verify the watcher behavior and compare process memory
on the same frozen Project used by AN-T-4012.

## Verification

The regression failed on the original watcher and passed after the
fix. All 27 focused Watcher, Archive, and Graph tests passed.
The same image and frozen Project, with only the watcher module
replaced, reduced Orchestrator's foreground peak from 463 to 68 MiB.
