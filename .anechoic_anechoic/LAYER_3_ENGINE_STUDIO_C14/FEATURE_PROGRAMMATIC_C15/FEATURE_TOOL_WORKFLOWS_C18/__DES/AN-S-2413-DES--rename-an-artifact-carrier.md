---
atom_family: SPEC
atom_id: AN-S-2413
structure:
  container:
    component: C18
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 26
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Rename an artifact carrier

## Scope

Generic Artifact rename orchestration and its boundary with logical Atom relocation.

## Claim

### Prose Claim

the framework **must** provide one deterministic generic Artifact Workflow that plans one artifact carrier rename under the active filename grammar, rejects collisions, plans governed canonical reference rewrites, records the identity mapping, **and** rolls back the complete rename **when** **any** required rewrite fails.

this Workflow owns generic naming and reference-rewrite policy and its admitted transaction safeguards, not connector mechanics. It supplies each exact storage target and delta, schema and authority bindings and expected state to the connector under CA-R-1936-CONNECTOR_TOOLS-RULE--use-one-coherent-connector-interface; the connector does not select names, references or recovery. `ATOM_MOVE` owns ANECHOIC Atom relocation, identity preservation, destination validation, one-Atom storage-effect safeguards **and** MCP-gated effect semantics; the generic Workflow **must not** become a public alternative for moving such Atoms. This generic rename contract does not add automatic incoming-reference retargeting to Atom replacement.

## Details
