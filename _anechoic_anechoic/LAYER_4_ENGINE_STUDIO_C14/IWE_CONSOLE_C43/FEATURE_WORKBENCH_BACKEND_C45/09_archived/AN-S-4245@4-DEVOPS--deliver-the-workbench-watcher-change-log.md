---
atom_family: SPEC
atom_id: AN-S-4245
container:
  component: C45
tier: 5
context:
  lens: DevOps
state:
  status: archived
  version: 4
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

Deliver the Workbench watcher change log

## Claim

### Prose Claim

Deliver one UTF-8 NDJSON file at `.anechoic_runtime/workbench/watcher-change-log.ndjson` and one read-only DuckDB `change_log` table. Both are technical derived state owned by the Workbench runtime and contain the same retained event set; neither is a business Journal or a source of Atom, Scope Unit or Relation facts. `query_schema` exposes `change_log` as a read-only table; graph mappings continue to use only `atoms` and `scope_units`.

The file and table expose only these event fields:

| Field | DuckDB type | Nullability | Meaning |
| --- | --- | --- | --- |
| `observed_at` | `TIMESTAMPTZ` | NOT NULL | Time at which the watcher observed the event. |
| `operation` | `VARCHAR` | NOT NULL | One of `create`, `update`, `rename`, `move` or `remove`. |
| `old_path` | `VARCHAR` | NULL | Repository-relative selected-source path before the event, when one exists. |
| `new_path` | `VARCHAR` | NULL | Repository-relative selected-source path after the event, when one exists. |

For `create` and `update`, `new_path` is present; for `remove`, `old_path` is present; for `rename` and `move`, both paths are present. A same-parent basename change is `rename`; a parent change is `move`, even when the basename also changes. Do not deliver identity, error, source-kind, content-hash, event-id, raw-source, Journal or graph-mapping columns.

The Workbench settings are:

- `ttl_hours`: fixed at `48` for both the file and table.
- `max_rows`: fixed at `100000` for both the file and table.
- cleanup: the existing owner's event-consumption loop short wait timeout, including while idle on the same owner thread, plus reread at owner start and on a full reread.

When the cap or TTL removes data, remove the oldest events from the file and table together. Do not report watcher-log failures as source-change events.


For a normal event batch without retention removal, append only additions to NDJSON and INSERT only those additions into DuckDB. Preserve duplicate observations. Retained-row replacement is limited to owner-start/full-reread reconciliation and actual TTL/cap cleanup. Keep the four-column public shape unchanged.
