---
atom_family: SPEC
atom_id: AN-S-2330
container:
  component: C46
tier: 4
context:
  lens: SWD
state:
  status: draft
  version: 8
  updated_at: '2026-11-13T20:51:06.160065+00:00'
---
## Summary

Use Tabulator for the Workbench read-only result grid

## Claim scope

Workbench frontend result-grid presentation and interaction.

## Claim

### Prose Claim

Use Tabulator 6.7.1 directly in Svelte. Add neither a wrapper nor a second grid engine. The grid is read-only: provide no cell or row editors or mutation actions.

Consume the backend View/grid/page contract over the complete materialized cache. Filtering, multisort, one-column grouping and exact row and group counts are global. The frontend consumes page slices and never reruns View SQL. In standalone and embedded modes, each Tab holds one query for execution under CA-R-2728. Historical View API identifiers remain compatible.

Expose only Cell Copy value, Cell Show full value, Row Copy row, Column Sort ascending/descending, Group by, Filter and Clear filter. Group by uses one column. Preserve positional columns and duplicate and dotted labels. Add no nested grouping, pivot, collaboration, persisted grid state or context-menu export. Adaptive/Fixed and Full/Limited affect presentation only; cache values remain unchanged. Shared result-file delivery stays outside this menu.

Each instance owns its callbacks. Wait for Tabulator's public table-built event before a data update. Invalidate queued refresh before destroy. Target deferred work only to its live instance. Use public lifecycle APIs without renderer patches.
