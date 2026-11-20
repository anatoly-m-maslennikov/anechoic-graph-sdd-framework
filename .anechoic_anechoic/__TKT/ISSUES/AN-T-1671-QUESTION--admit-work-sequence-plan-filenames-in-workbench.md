---
identity:
  atom_id: AN-T-1671
context:
  container:
    component: C14
  tier: 3
  template: question
state:
  status: active
  version: 1
  updated_at: 2026-11-11 19:26:12 +0400
---

## Summary

Admit Work Sequence Plan filenames in Workbench

## Concern

Should Workbench accept a Plan filename with its declared Work Sequence Number before the Project-prefixed Atom ID?

## Details

Current CA-D-469 allows this filename order. Workbench still requires the Project prefix at the start of the filename before it reads the Header. The native 001_backlog folders contain 50 Plans. Live query_run shows the 11 whose filenames start with the Atom ID and omits the 39 whose filenames start with a Work Sequence Number. Changing the Plan filename selection would make these Plans queryable without moving or renaming their carriers.
