---
atom_family: SPEC
atom_id: AN-S-2784
container:
  component: C45
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 4
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Generate canonical relation metadata from declarations

## Claim

### Prose Claim

Generate one rebuildable relation registry from Current Requirement relation Declarations for Workbench relation-name resolution and direct/derived materialization. Include canonical names, explicit inverse aliases, literal unqualified inverse bindings, and source IDs/versions. An inverse alias needs no separate Relation Declaration.

Normalize an explicit inverse by swapping endpoints once; preserve an unambiguous legacy named inverse through its declared counterpart without source edits or invented bindings. Derive container facts from effective Header.Container, including Context carrier layout, and resolve the Project root as `uppercase(Project prefix)-SU-00`. Build each inverse view once and refresh only affected rows/hashes on source change. Preserve exact model addresses: ambiguous/unsupported metadata is diagnosed and omitted, never guessed; prose, general CFEL and qualified derivation rules are not runtime facts.

Regenerate deterministic JSON metadata on every supported image rebuild, including local release, before image fingerprint/context assembly. Its fingerprint excludes a changing timestamp. A missing or failed asset prevents image/package acceptance rather than using handwritten/stale metadata. Relevant Current Declaration changes use the same compiler under existing owner synchronization; MCP tool discovery remains separate.
