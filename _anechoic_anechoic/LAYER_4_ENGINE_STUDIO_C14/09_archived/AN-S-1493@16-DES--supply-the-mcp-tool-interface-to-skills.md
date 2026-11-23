---
atom_family: SPEC
atom_id: AN-S-1493
container:
  component: C14
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 16
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Supply the MCP Tool interface to SKILLS

# Supply the MCP Tool interface to SKILLS

MCP supplies SKILLS with the current generated discovery **and** invocation interface for active Tools. Skills select **and** use that interface **without** redefining Tool behavior, while MCP preserves each Tool's identity, accepted inputs, structured outputs, **and** failure meaning.
