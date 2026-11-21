---
atom_family: SPEC
atom_id: AN-S-2784
container:
  component: C45
tier: 3
context:
  lens: SWD
state:
  status: draft
  version: 11
  updated_at: '2026-11-13T22:32:55.519808+00:00'
---
## Summary

Generate canonical relation metadata from declarations

## Claim

### Prose Claim

#### Registry

One rebuildable Workbench relation registry derives from Current Requirement relation Declarations. It contains canonical names, explicit inverse aliases, literal unqualified inverse bindings, and source IDs and Versions. An inverse alias does not need a separate Relation Declaration.

- Refresh mode uses Current Declaration inputs selected under CA-M-1011, including first-refresh bootstrap. Deterministic JSON is generated before image fingerprint and context assembly. The fingerprint excludes a changing timestamp.
- Existing mode uses the checkout registry unchanged. Missing or invalid assets and failed refresh prevent image or package acceptance.
- Startup loads the delivered registry. Declaration changes take effect after refresh and image rebuild. Source changes refresh relation facts under that registry. MCP tool discovery remains separate.

#### Fact admission

The build-time compiler reads runtime facts from supported code blocks in `Content.Claim.Formal Claim`. It ignores comments outside strings, unsupported relation expressions, and qualified derivation rules. Prose Claim, Semantics, Details, examples, and Header Topics supply no facts. Identity, lifecycle, and provenance select and bind inputs.

#### Resolution and refresh

Exact model addresses are preserved. Exact canonical names, declared inverse aliases or unique case-folded carrier spelling normalize once. Ambiguous or unsupported metadata and case-colliding carrier labels warn and omit affected facts, links and bindings without guessing.

- An explicit inverse swaps endpoints once; an unambiguous legacy named inverse uses its declared counterpart, without source edits or invented bindings. Each inverse view is built once.
- Container facts use effective `Header.Container`, including Context carrier layout. The Project root resolves to `uppercase(Project prefix)-SU-00`.
- References stay typed. Supporting source changes refresh only affected direct and derived facts, rows and hashes. Source bytes and Versions do not change.
