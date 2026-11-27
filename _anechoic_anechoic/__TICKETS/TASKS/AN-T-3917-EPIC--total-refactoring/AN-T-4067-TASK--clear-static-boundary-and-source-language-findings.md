---
atom_family: TKT
atom_id: AN-T-4067
container:
  atom: AN-T-3917
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-27T12:46:01+00:00'
---

## Summary

Clear Static boundary and source language findings

## Acceptance

Use the Realization Graph and the admitted Manifest checks. Clear
import ownership, Code Access, State and Source Language failures.
Keep test dependencies out of production, preserve existing exact
bypasses, and route imports to the owning Package. Coordinate
Spec Engine work with AN 1 and reuse AN-T-4062 and AN-T-4063.

## Progress

The working-checkout Manifest gate reports 0 denied or
unapproved imports after coordinated changes to the active Manifests.
The import ownership check passed after adding the Godot grouping entry.
The State check reports unresolved cases separately. Source Language
still flags the historical Workbench replay. Its TypeScript rename and
Spec Engine caller were handed to AN 1.
