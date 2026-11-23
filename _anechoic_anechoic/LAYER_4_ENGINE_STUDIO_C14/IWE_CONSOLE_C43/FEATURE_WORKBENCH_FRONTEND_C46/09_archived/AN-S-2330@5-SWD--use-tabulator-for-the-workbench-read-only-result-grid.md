---
atom_family: SPEC
atom_id: AN-S-2330
container:
  component: C46
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 5
  updated_at: 2026-11-10 00:46:37 +0400
---

## Summary

Use Tabulator for the Workbench read-only result grid

## Claim scope

Workbench frontend result-grid presentation and interaction.

## Claim

### Prose Claim

Use Tabulator 6.7.1 directly in the Svelte frontend as the Workbench result grid. Do not add a wrapper framework or a second grid engine. Keep the grid read-only: provide no cell or row editors and do not turn grid actions into mutations.

Use the existing backend Workbench View/grid/page contract against the complete materialized cached result. Backend filtering, multisort, one-column grouping and exact global row/group counts apply to the whole cached result, not only to the currently loaded page; the frontend consumes page slices and does not rerun the View query for display actions. Preserve one View as one query and use the same backend View context in standalone and embedded Workbench modes.

Expose only the approved read-only context actions: Cell Copy value, Cell Show full value, Row Copy row, Column Sort ascending, Column Sort descending, Group by, Filter and Clear filter. Group by is limited to one column in this MVP. Preserve positional columns, duplicate labels and dotted labels. Do not add nested grouping, pivoting, collaboration, editors or persisted grid state. No export action is added to the grid context menu; shared query-result file delivery remains available outside that context-action set. The Adaptive/Fixed row preference and Full/Limited content preference remain presentation-only; the full cached rows and values stay unchanged.

Each grid instance owns its pending browser callbacks. Wait for Tabulator's public table-built event before applying data updates. Invalidate queued refreshes before destroying an instance; a deferred update may target only its current live instance. Use public lifecycle APIs, without patching Tabulator renderer internals.

### Sources

- [Tabulator 6.x documentation](https://www.tabulator.info/docs/6.x)
- [Tabulator 6.x MIT license](https://www.tabulator.info/docs/6.x/license)
