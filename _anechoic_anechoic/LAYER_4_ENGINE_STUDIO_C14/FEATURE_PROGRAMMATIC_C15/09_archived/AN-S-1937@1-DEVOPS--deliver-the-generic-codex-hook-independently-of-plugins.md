---
atom_family: SPEC
atom_id: AN-S-1937
container:
  component: C15
tier: 6
context:
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Deliver the generic Codex hook independently of plugins

## Claim

### Prose Claim

Keep the generic hook source and its tests in the Project under CODEX_HOOK after that Scope Delegation is adopted. Deliver the host command and configuration independently of the Workbench plugin. Preserve unrelated host hooks.

The hook reads Codex JSON input and changes only the ANECHOIC request context. Test the receiving MCP schema and gateway together with the hook payload before enabling the installed host hook. Installation, host activation and a successful runtime call are separate checks.
