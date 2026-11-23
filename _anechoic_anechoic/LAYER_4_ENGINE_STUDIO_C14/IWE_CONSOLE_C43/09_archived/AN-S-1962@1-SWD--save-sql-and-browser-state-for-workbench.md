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
  version: 1
  updated_at: 2026-11-04 23:19:17 +0400
---

## Summary

Save SQL and browser state for Workbench

## Claim scope

Open SQL Worksheets, browser drafts and saved-query files.

## Claim

Save every open Worksheet's whole script and tab state in browser local storage every 5 seconds and restore it on the next page load. Ask before closing an unsaved tab or window; a native `beforeunload` warning is allowed. Flush the latest draft on `pagehide` and `beforeunload` when possible. Save Run and Check SQL through the shared `query_save` contract before execution, and save the whole script through `worksheet_save`. Load through `query_load` without execution, including when the reference is a URL. Keep browser drafts separate from immutable UTF-8 query and Worksheet files. Keep saved links in the current Workbench browser context; do not add cross-browser discovery or cross-app synchronization. Do not add sharing, authentication, deduplication, retry, repair, rollback, expiry or deletion workflows.
