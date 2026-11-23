---
atom_family: SPEC
atom_id: AN-S-1984
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 28
  updated_at: 2026-10-29 10:13:48 +0400
---
## Summary

Give Every Atom Revision One Content

## Claim scope

The Content of each Atom version.

## Claim

Each Atom version **must** have exactly one Content portion.

## Semantics

Content is the natural-language portion whose meaning generally requires
interpretation, represented by Markdown under the applicable D rules. Tools
can extract sections and check structure; that does not prove their meaning.
Structured YAML properties and operative formal rules are separate. A formal
Graph Rule can have only Summary in its Markdown Content, with optional
Semantics and Details; its fully formal Claim stays in its YAML `claim.*`
mapping. That does not require a duplicate `atom.content.claim`. Content does
not introduce another generic Substance field. The retained Summary's word
Revision refers to an Atom version, not a separate Revision entity.
