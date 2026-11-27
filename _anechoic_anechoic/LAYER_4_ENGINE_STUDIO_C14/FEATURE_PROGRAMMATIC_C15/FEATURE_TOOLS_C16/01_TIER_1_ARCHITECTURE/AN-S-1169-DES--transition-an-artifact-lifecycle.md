---
atom_family: SPEC
atom_id: AN-S-1169
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
  version: 22
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Transition an artifact lifecycle

# Transition an artifact lifecycle

the framework **must** provide one deterministic generic Artifact Tool that applies one registered artifact lifecycle transition, lazily creates its permitted destination directory, moves the carrier, updates required metadata **and** references, **and** fails closed on an undefined **or** ambiguous state model.

this Tool owns generic lifecycle-transition mechanics **only**. `ATOM_ARCHIVE`, `ATOM_PROMOTE`, `ATOM_UPGRADE`, **and** `CLOSE_ATOM` own their distinct ANECHOIC Markdown Atom transition meanings, validation, bulk rules **where** admitted, **and** MCP-gated effects; the generic Tool **must not** become a public alternative for those transitions.
