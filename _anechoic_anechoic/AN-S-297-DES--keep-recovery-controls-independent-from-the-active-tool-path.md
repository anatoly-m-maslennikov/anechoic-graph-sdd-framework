---
atom_family: SPEC
atom_id: AN-S-297
container:
  component: C00
tier: 1
context:
  lens: DES
state:
  status: active
  version: 12
  updated_at: 2026-10-27 19:59:56 +0400
---
## Summary

Keep recovery controls independent from the active Tool path

# Keep recovery controls independent from the active Tool path

the FPF Extension **must** provide one bounded manual recovery entrypoint for `status`, `stop`, `start`, **and** `reload` that remains operable **without** invoking an active Hook, Skill, MCP request, decision manager, **or** domain worker, **and** one independent automatic supervisor that **may** stop dispatch, restart a failed service within a declared budget, **or** open its circuit but **must not** perform **or** authorize domain effects; both control paths **must** preserve durable accepted work **and** report the exact selected release **and** process state.
