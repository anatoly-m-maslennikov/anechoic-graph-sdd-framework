---
atom_family: SPEC
atom_id: AN-S-1169
structure:
  container:
    component: C16
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 21
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Transition an artifact lifecycle

# Transition an artifact lifecycle

the framework **must** provide one deterministic generic Artifact Tool that applies one registered artifact lifecycle transition, lazily creates its permitted destination directory, moves the carrier, updates required metadata **and** references, **and** fails closed on an undefined **or** ambiguous state model.

this Tool owns generic lifecycle-transition mechanics **only**. `ATOM_ARCHIVE`, `ATOM_PROMOTE`, `ATOM_UPGRADE`, **and** `CLOSE_ATOM` own their distinct ANECHOIC Markdown Atom transition meanings, validation, bulk rules **where** admitted, **and** MCP-gated effects; the generic Tool **must not** become a public alternative for those transitions.
