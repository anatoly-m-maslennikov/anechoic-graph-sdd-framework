---
atom_family: SPEC
atom_id: AN-S-291
structure:
  container:
    component: C00
  tier: 1
context:
  lens: DevOps
state:
  status: active
  version: 14
  updated_at: 2026-10-27 19:59:25 +0400
---
## Summary

Encode exact Git references in release evidence

# Encode exact Git references in release evidence

**when** the GIT Extension supplies the Git binding for a selected release candidate, its evidence references **must** identify the repository **and** the full immutable commit object ID representing the checked content.

- a branch name, HEAD, **or** a tag name alone is **not** an exact Revision reference. retain a selected tag as a label **only** alongside its resolved commit ID.
- a commit ID **must not** represent uncommitted content as evaluated committed content; material working-tree differences **must** remain explicit under the applicable candidate binding.
- a release manifest **must** bind the released candidate **to** that exact reference; a later branch movement does **not** rebind earlier evidence.
- use the existing proof-frontier **and** Journal Carriers. do **not** create a second authoritative release log **or** redefine the generic Journal schema.

this Git-specific encoding does **not** select a branch strategy, require Git outside the selected Extension capability, **or** authorize commit, merge, tag, push, **or** publication.
