---
atom_family: SPEC
atom_id: AN-S-1384
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: active
  version: 27
  updated_at: "2026-11-23T01:48:06.176676+00:00"
---
## Summary

Bind MCP operation to the current project frontier

## Claim

### Prose Claim

Bind each MCP Tool call to one admitted Project identity and its installed code and configuration frontier. A single-Project service uses its fixed binding; a shared service requires an explicit Project for each call. Discovery across Projects is not itself a Project selection.

Backend owns Tool eligibility, validation, dispatch and the generated registry. MCP maps its enabled JSON catalog. Expose enough installed-code and registry provenance to diagnose currentness. Reject unresolved identity, cross-Project path escape or stale-registry invocation explicitly.

Registration and generic invocation do not reread source Atoms to establish currentness. Each Backend operation retains its own source and business validation.
