---
identity:
  atom_id: AN-S-2533
context:
  container:
    component: C16
  tier: 4
  lens: DevOps
state:
  status: active
  version: 17
  updated_at: '2026-11-13T19:34:13.426921+00:00'
---
## Summary

Bind graph projection Tool carriers

## Claim

### Prose Claim

The declared existing Tool entrypoint and RMED packet for the two graph builders.

The bounded packet **must** keep `GENERATE_ENTITY_GRAPH` as the single declared Tool carrier while exposing separate Entities and Terms graph namespaces.

## Details

```toml
[tool_binding]
name = "GENERATE_ENTITY_GRAPH"
entrypoint = "LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/generate_entity_graph.py"
mcp_name = "generate_entity_graph"
action_ids = ["CA-O-134", "CA-O-137"]
graph_kinds = ["entities", "terms"]
```

The `mcp_name` above is a declared Tool binding, not evidence that that name is registered, exposed or admitted by a connected server. `action_ids` identify the existing projection Actions for the two graph kinds. The existing selected Workflow entrypoints are `build_entities_graph` for CA-O-133/CA-O-135/CA-O-134 and `build_terms_graph` for CA-O-136/CA-O-138/CA-O-137; those Workflow and Step references are context, not Action mappings. Their executable request schemas and exact source bindings come from current admitted discovery/context and the canonical selected manifest. A declared carrier, available source file or listed public route name alone does not establish executable admission; an unavailable binding remains unavailable rather than inviting a guessed call or another graph engine.

Both Workflows reuse this single Tool implementation and the CA-D-661 boundary; this carrier does not register a duplicate MCP gateway or prescribe new request/context grammar. Any admitted derived fact context remains source-bound input, not a new source authority. Implementation remains gated on independent corrected RMED review under CA-D-540.
