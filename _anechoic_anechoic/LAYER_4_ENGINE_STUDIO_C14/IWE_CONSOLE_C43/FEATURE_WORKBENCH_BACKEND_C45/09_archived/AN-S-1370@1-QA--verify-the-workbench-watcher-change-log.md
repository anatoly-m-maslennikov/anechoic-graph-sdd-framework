---
atom_family: SPEC
atom_id: AN-S-1370
container:
  component: C45
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 18:48:47 +0400
---
## Summary

Verify the Workbench watcher change log

## Claim

### Prose Claim

With the existing server `watchdog` Observer observing only a selected repository `control_root`, verify that the file and DuckDB table retain the same technical event rows:

| Case | Expected result |
| --- | --- |
| A selected source file is added, modified or deleted | One corresponding `create`, `update` or `remove` record with the appropriate new or old repository-relative path. |
| A native `on_moved(src_path, dest_path)` callback changes the basename in the same parent | One `rename` record with the callback's old and new paths. |
| A native `on_moved(src_path, dest_path)` callback changes the parent | One `move` record with the callback's old and new paths, even when the basename also changes. |
| A native move enters or leaves the watched `control_root` | Entering produces `create` with `new_path`; leaving produces `remove` with `old_path`. |
| A native callback reports a selected directory create, move or remove | Record the observed directory operation and refresh the index; do not record directory modification noise. |
| An add/delete pair occurs without a native move callback | Do not promote the pair to `rename` or `move`. |
| A change occurs outside the selected repository source folder | No change-log row. |
| A grouped watcher batch contains several observations | Preserve each observed operation; do not invent a Workflow or business Journal record. |
| An event reaches 48 hours of age | The existing owner event-consumption loop's short wait timeout, including while idle on the same owner thread, removes it from both the NDJSON file and `change_log`; no stale copy remains queryable after cleanup. |
| The 100,000-row cap is exceeded | Remove the oldest events from both stores until the same retained set has at most 100,000 rows. |
| The owner restarts or performs a full reread | Reread retained log rows, preserve still-live events, and apply the same 48-hour TTL and 100,000-row cap. |
| The watcher is idle | The existing owner event-consumption loop's short wait timeout performs cleanup on the same owner thread; no separate watcher service, Workflow scheduler, retry or recovery path is started. |
| A source or log write fails | Keep the existing error boundary; do not create an `error` event row or Journal entry. |

Run a real Docker end-to-end check on a bind-mounted temporary repository and selected `control_root`. Perform actual file creation, modification, same-parent rename, parent-changing move, and selected-directory move operations while the Observer is running; verify native callback paths, observed directory create/move/remove handling, and matching file/table rows. Keep the owner idle through the event-consumption loop's short wait timeout and verify 48-hour expiry in both stores using the real runtime path. Do not fabricate paired add/delete events or call an internal callback directly.

Verify that `change_log` is not used as an `atoms`/`scope_units` source, graph vertex or Relation fact, and that the delivered columns are limited to `observed_at`, `operation`, `old_path` and `new_path`.
