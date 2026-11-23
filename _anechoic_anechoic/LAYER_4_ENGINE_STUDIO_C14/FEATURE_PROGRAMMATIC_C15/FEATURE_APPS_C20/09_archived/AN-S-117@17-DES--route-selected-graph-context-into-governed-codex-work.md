---
atom_family: SPEC
atom_id: AN-S-117
container:
  component: C20
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 17
  updated_at: 2026-10-24 13:39:34 +0400
---
## Summary

Route selected graph context into governed Codex work

# Route selected graph context into governed Codex work

`CODEX_PLUGIN` **must** let an operator transfer the canonical identities, paths, current digests, **and** declared selection boundary of GRAPH_UI nodes into a Codex conversation, ask questions about that bounded context, **and** request applicable ANECHOIC work through existing Skills **and** the provider-neutral MCP Tool interface. The plugin **must not** implement project mutation itself, widen the selected scope implicitly, bypass Tool validation **or** host permissions, expose secrets, **or** perform an irreversible action **without** the host's required operator confirmation; results **must** preserve Tool meaning, provenance, **and** explicit failure states.
