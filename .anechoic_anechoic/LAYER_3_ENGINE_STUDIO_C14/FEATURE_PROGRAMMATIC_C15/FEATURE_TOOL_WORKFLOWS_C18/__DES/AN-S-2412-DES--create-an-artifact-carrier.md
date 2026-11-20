---
atom_family: SPEC
atom_id: AN-S-2412
structure:
  container:
    component: C18
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 28
  updated_at: 2026-10-27 19:59:50 +0400
---
## Summary

Create an artifact carrier

## Scope

Generic Artifact construction orchestration and its boundary with logical CreateAtom.

## Claim

### Prose Claim

the framework **must** provide one deterministic generic Artifact Workflow that selects the canonical identity **and** filename required by the admitted Artifact Carrier schema **and** creates one Carrier from its structural owner **and** the inputs required by that schema, **without** silently overwriting an existing Carrier.

this Workflow owns generic construction, identity and naming decisions, not connector mechanics. Its connector receives the complete explicit target and content, supplied schema and authority bindings and expected absence under CA-R-1936-CONNECTOR_TOOLS-RULE--use-one-coherent-connector-interface; it does not allocate identity or choose ownership. `ATOM_CREATE` owns ANECHOIC Atom admission, stable-identity, revision, per-Atom preflight **and** MCP-gated effect semantics; the generic Workflow **must not** become a public alternative for creating such Atoms.

## Details
