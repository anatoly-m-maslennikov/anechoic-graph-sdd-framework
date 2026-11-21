---
atom_family: SPEC
atom_id: AN-S-2394
container:
  component: C16
tier: 4
context:
  lens: DevOps
state:
  status: active
  version: 14
  updated_at: 2026-11-02 19:46:47 +0400
---
## Summary

Bind Journal query source route to one Tool

## Scope

The one-route binding.

## Claim

### Prose Claim

The delivered Journal query Tool **must** bind CA-O-161, CA-O-163, and CA-O-162 as one route without defining a second Workflow, Action, or Journal.

## Details

```toml
[tool_binding]
name = "FIND_AND_FETCH_JOURNAL_EVENTS"
entrypoint = "LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FIND_AND_FETCH_JOURNAL_EVENTS/find_and_fetch_journal_events.py"
action_ids = ["CA-O-162"]
workflow_ids = ["CA-O-161"]
mcp_name = "find_and_fetch_journal_events"
```

This discovery binding identifies the existing read-only Tool and its existing
MCP route. MCP and orchestrator registration remain separate delivery work;
the binding creates no Workflow, Action, Run, or Journal.
