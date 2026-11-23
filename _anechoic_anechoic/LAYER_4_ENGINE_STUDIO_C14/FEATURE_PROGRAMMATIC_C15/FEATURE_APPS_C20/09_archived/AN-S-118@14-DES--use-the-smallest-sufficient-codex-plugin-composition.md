---
atom_family: SPEC
atom_id: AN-S-118
container:
  component: C20
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 01:28:26 +0400
---
## Summary

Use the smallest sufficient Codex plugin composition

# Use the smallest sufficient Codex plugin composition

`CODEX_PLUGIN` **must** contain **only** the Codex-host capabilities necessary **to** expose the current `GRAPH_UI` **and** route governed ANECHOIC work: skills for repeatable workflow guidance, a connection **to** the provider-neutral `MCP` unit **only** **when** Tool invocation is required, UI **only** **when** graph inspection **or** navigation materially benefits from it, **and** hooks **only** for Codex-specific lifecycle behavior. Every MCP-backed capability **must** remain usable **without** UI, **and** the plugin **must** reference rather than duplicate provider-neutral Skill, Tool, MCP, GRAPH_UI, **or** Methodology behavior.
