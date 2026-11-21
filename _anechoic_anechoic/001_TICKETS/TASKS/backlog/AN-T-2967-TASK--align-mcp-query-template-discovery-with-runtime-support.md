---
atom_family: TKT
atom_id: AN-T-2967
container:
  component: C21
priority: 2
context:
  template: task
  label: Task
state:
  status: "backlog"
  version: 1
  updated_at: "2026-11-21T20:10:12.833390+00:00"
---
## Summary

Align MCP query template discovery with runtime support

## Details

The exposed `query_template` schema lists `resolve_legacy_ref` and `resolve_legacy_path`. Both supplied operations return `rejected` with `tool_input_invalid`. The schema also omits `in_queue` and `complete` from the status filter, although the Workbench schema lists both and `list_tickets` accepts `in_queue`. In the live Project probe, that filter returned 36 Tickets. The advertised `active` filter returned zero.

## Acceptance Criteria

- The MCP discovery schema and help list the templates and arguments that the runtime supports.
- The advertised status filter includes the supported Ticket statuses, including `in_queue`.
- A discovery-to-runtime check covers the exposed template names and status filter values.
