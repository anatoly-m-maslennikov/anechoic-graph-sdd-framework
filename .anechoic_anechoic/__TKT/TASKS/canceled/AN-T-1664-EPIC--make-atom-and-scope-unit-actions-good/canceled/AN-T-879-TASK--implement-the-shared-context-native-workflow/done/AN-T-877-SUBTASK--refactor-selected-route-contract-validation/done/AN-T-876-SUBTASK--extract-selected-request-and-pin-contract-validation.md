---
atom_family: TKT
atom_id: AN-T-876
structure:
  container:
    atom: AN-T-877
  priority: 2
context:
  template: task
  label: Subtask
state:
  status: done
  version: 6
  updated_at: 2026-11-02 19:44:26 +0400
---
# Summary

Extract selected request and pin contract validation

## Objective

Separate request/pin validation and canonical serialization into cohesive bounded modules, preserving closed schemas, exact digest/error behavior, source guards and all declared public/private compatibility imports.

## Details

The Operator explicitly refused a source-size exception and selected refactoring legacy files first. Every leaf is at most 15 minutes own work; split before expanding. New or materially changed Python files must meet the applicable <=200 physical-line target and small cohesive unit boundaries; no mixin/namespace class or imported-method facade substitutes for responsibility decomposition. Preserve the pinned C901/format/lint and applicable typing baseline. Use the locked Project virtual environment, disable bytecode writes and keep disposable test state below configured Project Temporary State. Do not revert other workers' changes. One Task per file, exact predecessor history; review/update dependants after each completed Task.

Accepted request/pin extraction: canonical SelectedRouteError and all historic definitions remain import-compatible. Exact malformed versus stale definition_manifest failures are preserved and covered by a new functional regression test. The query admission mapping is externalized as an exact tuple-of-dicts JSON value and duplicate definition sequencing was removed. Independent architecture re-review closed all three findings. No terminal semantics or current manifest admission changed.

### Definition of Done

Retain actual before/after focused tests, changed paths, source/unit/complexity measurements and explicit unresolved limits. Preserve frozen test oracle bytes and current public behavior before new shared-context feature work. No production MCP, release, deployment, full suite, source-policy edits or Git publication.
