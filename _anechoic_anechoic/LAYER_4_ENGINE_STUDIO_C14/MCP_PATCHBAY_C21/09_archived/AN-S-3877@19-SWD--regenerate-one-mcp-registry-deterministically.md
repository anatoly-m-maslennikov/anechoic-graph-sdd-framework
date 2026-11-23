---
atom_family: SPEC
atom_id: AN-S-3877
container:
  component: C21
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 19
  updated_at: 2026-10-27 19:59:40 +0400
---
## Summary

Regenerate one MCP registry deterministically

# Regenerate one MCP registry deterministically

## Applicable when

Apply after one installed runtime activation **or** a declared descriptor refresh requires a new registry generation.

## Procedure

1. Reopen the active installed package/image selection and seal its complete Tool descriptor frontier under `CA-D-621-TOOLS-DELIVERY--encode-uniform-tool-self-description`; do not derive a live frontier from a checkout.
2. Run the registered Tool descriptor-generation script, validate descriptors independently, and derive the valid registry without a handwritten MCP-core allowlist.
3. Order equivalent inputs stably, publish the valid registry and unavailable-capability diagnostics atomically as one generation, and record the prior and active generation identities.
4. Repeat generation against an unchanged frontier and compare semantic registry content while excluding volatile execution metadata. Emit a change notification when supported, while retaining client refresh as unconfirmed until observed.

## Outcome

The same activated installed descriptors and Project state produce the same MCP capability registry without capability execution.

## Failure or stop

Stop **when** installed-selection reopening, generator integrity, ordering, identity, or repeated semantic output is **not** deterministic. Quarantine an individual invalid descriptor under CA-M-172.
