---
atom_family: SPEC
atom_id: AN-S-2411
container:
  component: C18
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 26
  updated_at: 2026-10-27 19:59:50 +0400
---
## Summary

Patch artifact metadata

# Summary

Patch artifact metadata

## Scope

Generic Artifact metadata-patch orchestration and its boundary with logical Atom Modify.

## Claim

the framework **must** provide one deterministic generic Artifact Workflow that derives a schema-validated field-level patch **to** one artifact's frontmatter, preserves its body bytes, decides governed revision metadata, **and** rejects unknown fields **or** failed preconditions before delegating the explicit storage delta.

this Workflow owns form-agnostic patch and revision policy, not connector mechanics. Its connector receives only explicit content or edits, supplied schema and authorization context and expected state under CA-R-1936-CONNECTOR_TOOLS-RULE--use-one-coherent-connector-interface; the connector makes no revision or lifecycle decision. The generic procedure **must not** be exposed **or** applied as a substitute for `ATOM_UPDATE` **to** a ANECHOIC Markdown Atom; the Atom Workflow owns that Atom's target resolution, authority validation, revision transition, one-Atom storage-effect safeguards **and** MCP-gated effect, **and** **may** use this procedure **only** as an internal helper.

## Details
