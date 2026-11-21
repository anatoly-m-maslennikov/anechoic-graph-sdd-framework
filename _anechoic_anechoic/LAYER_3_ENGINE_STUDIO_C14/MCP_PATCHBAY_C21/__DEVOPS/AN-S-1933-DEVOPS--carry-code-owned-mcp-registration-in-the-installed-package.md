---
atom_family: SPEC
atom_id: AN-S-1933
container:
  component: C21
tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 6
  updated_at: '2026-11-12T12:32:31.781804+00:00'
---
## Summary

Carry code-owned MCP registration in the installed package

## Claim

### Prose Claim

The MCP package carries tool_providers.json as its code-owned provider inventory, generate_tool_registry.py as generator, and tool_registry.json as generated runtime registration asset in FEATURE_MCP. The generator accepts --package-root, reads inventory and installed provider code, and never reads Project Atom carriers or executes a capability; equivalent installed inputs produce equivalent bytes using canonical descriptors, models, and adapters.

In refresh mode, generate the asset in the staged package before final inventory verification and image build. In existing mode, copy the checkout asset unchanged. Include its bytes in the package and image identities. A missing asset or failed refresh stops delivery before startup. Direct source development uses the same asset/generator. Do not add a daemon, watcher, Workflow scheduler, or Atom fallback.

Inventory carries provider keys, implementation/factory symbols, descriptor factories, and explicit global mcp_blacklist; generated data carries resolved provider/Tool registration and exclusions. Keep these as configuration files, not a fixed Python Tool-name list. The installed adapter distribution keeps its version-bound interface declaration at the existing MCP Delivery location; use canonical descriptor/model symbols, preserve protocol revision/capability/result meanings, and keep declarations, schemas, and examples credential-free. Registration/schema generation grants no effect permission.

The version-bound interface declaration carries the supported protocol revision and capabilities, admitted progress/cancellation/correlation/resource-bound fields, and existing result meanings. Derive its descriptor schema only from installed canonical model symbols; accept no caller-supplied descriptor schema. Registration, schema derivation, projection and refresh never invoke a capability, start a Workflow or infer approval. Keep declarations, schemas and examples credential-free.
