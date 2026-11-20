---
atom_family: SPEC
atom_id: AN-S-1168
structure:
  container:
    component: C16
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 22
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Read artifact metadata

# Read artifact metadata

the framework **must** provide one deterministic generic Artifact Tool that returns selected frontmatter fields **and** derived carrier identity for one artifact **without** loading its body, with explicit results for absent fields **and** parse errors.

this Tool owns form-agnostic metadata retrieval **only**. it does **not** define ANECHOIC Markdown Atom selector, lifecycle, identity, **or** output-view semantics; **when** used for an Atom, `ATOM_READ` owns the public Atom operation **and** **may** use this Tool **only** as a helper.
