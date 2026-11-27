---
atom_family: SPEC
atom_id: AN-S-2496
container:
  component: C18
tier: 2
context:
  lens: DevOps
state:
  status: active
  version: 15
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---
## Summary

Deliver shared TOML and configuration workflows

## Scope

Apply the shared connector boundary in AN-S-2478.

The required shared TOML connector and configuration-specific workflow delivery contract under TOOL_WORKFLOWS. It establishes no additional configuration connector, storage backend or runtime path.

## Claim

### Prose Claim

One shared TOML connector under CONNECTOR_TOOLS supplies CA-O-218 complete Read under CA-D-631 and CA-O-204 Modify under CA-D-625. Apply AN-S-2417 to Project Structure and Project Settings Workflow authority.

## Details

Within the existing service envelope, a configuration workflow carries its explicit configuration kind, admitted logical source identity, exact expected source revision/digest, complete proposed TOML delta and applicable schema/validation evidence. The workflow parses and validates the complete proposed configuration before its effect; the connector verifies the supplied admission evidence and rechecks expected source state and permission without choosing the schema. No arbitrary filename or configuration kind can grant authority. Project Structure and Project Settings retain their configured authoritative TOML identities; their workflows reject generated/protected field edits and preserve unrelated values. Configuration-source bindings remain private adapter details, not new connector identities.

Apply AN-S-2425 to the complete Read, its source-state evidence as input to proposal validation, and the subsequent Modify. Project Structure changes, including Scope Unit Create, use the structural schema. Project Settings changes follow the settings schema. CA-O-205 uses CA-O-219 before CA-O-209. CA-O-206 uses CA-O-220 before CA-O-210. The Read Steps call CA-O-218, and the patch Steps call CA-O-204. Neither Workflow reads storage directly or assumes Modify implies Read. The connector returns the exact bound state and proposed or observed result with its source-state evidence.

Return actual source revision/effect observations and explicit validation, stale, denied, failed, uncertain or no-op results through the existing shared result/recording contract. Physical TOML carrier names remain current adapter bindings. Preserve prior admitted configuration and accepted history within each action's claimed safety boundary; a serialization contract does not prove atomic publication.

### Delivery status

This is required future delivery, not implementation, installation, admitted MCP routing, DB support or stronger concurrency/publication proof. Configuration workflows do not multiply connectors. New workflow resume/retry and previously deferred publication/concurrency work remain deferred.
