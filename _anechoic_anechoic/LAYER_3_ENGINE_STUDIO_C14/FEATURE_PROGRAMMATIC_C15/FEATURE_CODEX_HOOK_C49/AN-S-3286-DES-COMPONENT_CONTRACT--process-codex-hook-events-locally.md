---
atom_family: SPEC
atom_id: AN-S-3286
container:
  component: C49
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-21T18:44:22.234679+00:00'
---

## Summary

Process Codex Hook events locally

## Guarantee

Given a Codex `PreToolUse` event on standard input, return one JSON
response on standard output. For an ANECHOIC MCP request, bind the
supplied absolute session folder and session ID to the request. Deny
malformed or conflicting input. Return an empty response for other
Tools.

The Hook uses host input and output only. It imports zero other
Project Components and makes zero outbound calls.

## References

AN-S-2621, AN-S-3052, and AN-T-2944.
