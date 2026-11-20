---
identity:
  atom_id: AN-T-2005
context:
  container:
    component: C43
  tier: 3
  template: problem
state:
  status: resolved
  version: 3
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

The deployed MCP rejects current query parameters.

## Concern

The running MCP used the older query schema and rejected `preview: 0` and
`save: false`, even though the current source supported them. Source tests alone
did not establish deployed adoption.

## Resolution

The tested 0.4.4.22 image is running on port 56317. After the release startup
failed in an empty Python environment, the existing Project bootstrap restored
MCP using the tested installed package and its provisioned launcher environment.

A fresh native MCP SDK client confirmed that `query_run` advertises `preview`
and `save` and accepts `preview: 0, save: false`. It returned zero rows and one
column without creating a saved query. Workspace/View create, SQL update,
metadata-only Run, five-row fetch, focus and query-log checks also passed.

The endpoint verification is recorded in
`.anechoic_tmp/workbench/codex-extension/live-proof.json`. The automated
release-caller correction and catalog completion remain separate work; the
query-parameter deployment mismatch itself is resolved.
