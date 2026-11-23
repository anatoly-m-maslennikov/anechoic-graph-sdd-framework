---
atom_family: SPEC
atom_id: AN-S-1962
container:
  component: C43
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 5
  updated_at: 2026-11-05 14:23:38 +0400
---

## Summary

Save SQL and browser state for Workbench

## Claim scope

Open SQL Views, browser drafts and saved-item Journal records.

## Claim

Save every open View's whole script, current local View name and tab state in browser local storage every 5 seconds and restore it on the next page load. Ask before closing an unsaved tab or window; a native beforeunload warning is allowed. Flush the latest draft on pagehide and beforeunload when possible.

Run and Check do not save SQL or create Journal records. Query saving is the combined Run & Save operation: it executes successfully first, then writes the exact selected SQL and optional creation name to the saved-item Journal. A failed query creates no saved entry. If saving fails after the Run succeeds, keep the completed result, its query ID, the previous saved identity and the dirty state; show the save error and do not retry or roll back. Save View remains the whole-script View operation and may persist its optional name.

Load through query_load without execution, including when the reference is a URL. Keep browser drafts separate from the Project-level saved-item Journal. Keep saved links in the current Workbench browser context; do not add cross-browser discovery or cross-app synchronization. Saved-item Journal writes use the existing date-partitioned workbench-saved-items writer and are excluded from source watching, so explicit saving does not trigger Atom reindexing. Do not add sharing, authentication, deduplication, retry, repair, rollback, expiry or deletion workflows.

Use Python 3.14 standard-library uuid.uuid7() for new saved-entry IDs. Do not add a UUID library. Store saved_query_id, kind, exact sql, optional name and saved_at in each Journal row. New View entries use kind view. Existing saved entries with kind worksheet and existing runtime q_/w_ files remain read-only compatibility sources.

Persist the selected Compact or Comfortable density with the existing Theme, text Zoom and workspace settings. Compact is the default for 13–14 inch displays; Comfortable is for 20 inch displays. The Operator selects the setting; do not detect physical screen size automatically. Keep text Zoom independent from density. Persist Chat position (Left or Right, default Right), the current Work/Chat split and divider width with those settings. Restore them and allow keyboard-accessible Widen chat and Narrow chat commands on either side without adding a second state store.
