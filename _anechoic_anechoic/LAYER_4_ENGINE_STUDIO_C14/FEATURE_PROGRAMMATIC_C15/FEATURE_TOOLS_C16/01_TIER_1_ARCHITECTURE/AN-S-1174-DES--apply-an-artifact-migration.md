---
atom_family: SPEC
atom_id: AN-S-1174
concern:
  subject: "Artifact"
  path: "Model/Graph/Node"
  relation: "is_narrower_than"
container:
  component: C16
tier: 1
context:
  lens: DES
state:
  status: active
  version: 23
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Apply an artifact migration

# Apply an artifact migration

the framework **must** provide one deterministic generic Artifact Tool that applies one approved migration plan **only** **when** its recorded preconditions still match, commits **all** carrier **and** reference mutations as one rollbackable transaction, **and** appends the governed migration event through the Work Journal Tool.

this Tool owns generic migration-transaction mechanics **only**. `MIGRATE_ATOM_IDENTITY` **and** `REBIND_ATOM_RELATIONS` own their sealed ANECHOIC Markdown Atom migration **and** rebinding semantics, including their exact source, revision, relation, **and** MCP-gated effect boundaries; the generic Tool **must not** become a public alternative for those Atom changes.
