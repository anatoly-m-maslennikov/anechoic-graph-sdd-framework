---
atom_family: SPEC
atom_id: AN-S-3715
container:
  component: C20
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 13
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

execute Agent proposals **in** an isolated service

## Claim

### Prose Claim

This retained contract applies only when AI-Agent execution is separately admitted. It does not enable that execution or claim that its runtime implementation is present.

execute an Agentic Action by sending its bound context **to** the private Agent service **and** admitting the returned proposal through the existing worker boundary.

## Details

### Scope

the worker's replaceable Agent adapter **in** the Docker runtime.

- use a bounded JSON request carrying context, check **or** fix phase **and** timeout; admit the existing AgentOutput schema.
- provide **only** the compiled context, not Project mounts. run Codex CLI **in** a fresh dispatch directory with no inherited user configuration **or** MCP registrations.
- the dedicated Agent container provides outer isolation; the CLI can use external isolation there. native execution retains its read-only CLI sandbox.
- allow **<=1** active Agent request initially. bound request bytes, response bytes **and** execution duration.
- preserve accepted output before effects. transport loss, timeout, invalid output **or** authentication failure interrupts rather than silently retrying.
- seed an absent private runtime authentication cache from an explicitly mounted credential file. do **not** overwrite an existing refreshed cache **or** print its contents.
