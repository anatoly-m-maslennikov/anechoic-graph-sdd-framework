---
atom_family: SPEC
atom_id: AN-S-3286
container:
  component: C49
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3052
state:
  status: active
  version: 3
  updated_at: '2026-11-22T22:21:55.393137+00:00'
---

## Summary

Process Codex Hook events locally

## Guarantee

The Hook is installed in user-global Codex configuration and matches ANECHOIC MCP requests only. Given a Codex `PreToolUse` event on standard input, it returns one JSON response on standard output. It returns an empty response for other Tools.

For an ANECHOIC MCP request, resolve the event's absolute `cwd` through the local filesystem. Find the nearest canonical Git worktree root by walking upward to a `.git` directory or file marker. Bind that root and the event's session ID to the request.

Deny malformed or conflicting input, a missing worktree root, or an explicit Project root that does not match the resolved root. Deny a caller session ID that conflicts with the event's session ID.

The Hook makes no subprocess or other Component calls. It uses local filesystem access and host input and output.

## References

AN-S-2621, AN-S-3052, and AN-T-2944.
