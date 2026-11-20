---
atom_family: TKT
atom_id: AN-T-1520
structure:
  container:
    atom: AN-T-1525
  priority: 2
context:
  template: task
  label: Subtask
state:
  status: done
  version: 7
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Reject standalone CLI mutations

## Objective

reject standalone CLI apply before writes, preserving preview and the existing admitted selected/MCP native mutation functions.

## Details

- keep this repair bounded to its confirmed source contract. shared installed runtime, frozen candidates and historical Journals remain unchanged by fixture tests.
- preserve independent workers' edits; root owns Git, source pins and Release integration.

## Definition of Done

both executable wrappers reject direct apply without filesystem effects; preview and admitted native behavior retain coverage.

## Result

the canonical executable wrappers refuse standalone apply before repository resolution and writes. the 26-test focused suite passes, including actual subprocess refusal and preview zero-write checks; independent source/code review accepts the bounded repair. actual full Release completion remains a separate unfinished gate.
