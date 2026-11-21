---
atom_family: TKT
atom_id: AN-T-2927
structure:
  container:
    component: C14
  priority: 2
context:
  template: task
  label: Epic
state:
  status: draft
  version: 1
  updated_at: '2026-11-20T15:46:41.967457+00:00'
---

## Summary

Unify Engine diagnostic output

## Objective

Make process output the single source of truth for Engine errors, warnings,
info, and debug messages. Apply the same rules to requests, the SAM daemon,
FileWatcher, and other background components.

## Work

### Stage 1. Prepare the Spec

1. Create Tier 1 Policy Draft AN-S-3158@1.
2. Update AN-S-1902 and AN-S-1343 for diagnostic emission and delivery.
3. Update AN-S-1310 for acceptance across requests and background components.

## Definition of Done

The Engine uses the existing diagnostic path. Every failed HTTP or MCP
request reports the error to the caller and to process output. Verify the
same process output for daemon and watcher failures, with MCP stdio reserved
for protocol messages.

## Status

The Tier 1 Policy is prepared in Draft.
