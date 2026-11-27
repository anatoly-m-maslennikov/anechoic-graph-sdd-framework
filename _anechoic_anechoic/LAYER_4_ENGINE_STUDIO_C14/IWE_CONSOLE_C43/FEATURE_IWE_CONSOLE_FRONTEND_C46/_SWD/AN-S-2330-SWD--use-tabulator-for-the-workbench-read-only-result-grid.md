---
atom_family: SPEC
atom_id: AN-S-2330
container:
  component: C46
tier: 4
context:
  lens: SWD
state:
  status: active
  version: 7
  updated_at: '2026-11-12T12:34:28.903393+00:00'
---
## Summary

Use Tabulator for the Workbench read-only result grid

## Claim scope

Workbench frontend result-grid presentation and interaction.

## Claim

### Prose Claim

Use Tabulator 6.7.1 directly in Svelte; add neither wrapper nor second grid engine. Grid is read-only: no cell/row editors or mutation actions. Consume backend View/grid/page contract over the complete materialized cache: filtering, multisort, one-column grouping and exact row/group counts are global, while frontend consumes page slices and never reruns View SQL. In standalone and embedded modes, each Tab holds one query for execution under CA-R-2728; historical View API identifiers remain compatible.

Expose only Cell Copy value, Cell Show full value, Row Copy row, Column Sort ascending/descending, Group by, Filter and Clear filter. Group by is one column. Preserve positional columns and duplicate/dotted labels; add no nested grouping, pivot, collaboration, persisted grid state or context-menu export. Adaptive/Fixed and Full/Limited are presentation-only; cache values remain unchanged and shared result-file delivery stays outside this menu.

Each instance owns callbacks. Wait for Tabulator public table-built before data update, invalidate queued refresh before destroy and target deferred work only to its live instance. Use public lifecycle APIs without renderer patches.
