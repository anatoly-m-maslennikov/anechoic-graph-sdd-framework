---
atom_family: SPEC
atom_id: AN-S-1376
structure:
  container:
    component: C46
  tier: 5
context:
  lens: QA
state:
  status: active
  version: 6
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify Workbench result-display preferences

## Claim scope

The Workbench frontend's result sizing and content presentation remain user-controlled, persisted, and query-stable.

## Claim

### Prose Claim

In a real browser, start with a paged result and value over 150 Unicode characters. Defaults are Adaptive rows and Limited N=150; Fixed retains 100 and reveals its numeric field only when selected. Fixed accepts persisted positive 1..1000 page size; invalid values preserve prior choice, and Adaptive hides the field/fits available area through resize and all zoom/Density changes without losing result. Display-only changes and later pages reuse query ID/page flow without rerunning SQL.

Limited/Full is one persisted canonical preference available from Settings, ResultsTable header and palette. Limited displays exactly first positive-N Unicode characters; Full hides N while returned value remains whole. Verify Dark readable names/muted types and Tabulator states, pre-wrap every source newline, and cached-result resize/grid leave/rebuild without uncaught delayed callback. CA-E-786 owns exact action matrix/one-column grouping/global cache semantics. Pass only with browser-visible preference persistence, query stability and no uncaught error.
