---
atom_family: SPEC
atom_id: AN-S-1168
container:
  component: C16
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 13
  updated_at: 2026-10-24 00:28:02 +0400
---
## Summary

Read artifact metadata

# Read artifact metadata

the framework **must** provide one deterministic generic Artifact Tool that returns selected frontmatter fields **and** derived carrier identity for one artifact **without** loading its body, with explicit results for absent fields **and** parse errors.

this Tool owns form-agnostic metadata retrieval **only**. it does **not** define ANECHOIC Markdown Atom selector, lifecycle, identity, **or** output-view semantics; **when** used for an Atom, `ATOM_READ` owns the public Atom operation **and** **may** use this Tool **only** as a helper.
