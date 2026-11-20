---
atom_family: SPEC
atom_id: AN-S-1984
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 34
  updated_at: '2026-11-12T02:58:47.673536+00:00'
---
## Summary

Give Every Atom Revision One Content

## Claim

### Prose Claim

Applicability: The Content of each Atom version.

Each Atom version **must** have exactly one Content portion.

## Semantics

Content is the Markdown portion whose natural-language meaning generally needs interpretation. Header properties use YAML. A complete ordinary RMED Content portion has a Claim grouping with no direct value and one or both declared Formal Claim and Prose Claim children. Formal Claim uses the fenced language admitted by its declaration. Prose Claim contains ordinary Markdown. Tools can extract declared Properties or parse supported formal syntax without proving all prose meaning.

One Content portion is a structured group with zero direct scalar values and independently counted child Properties. This introduces no generic Substance field. The retained Summary's word Revision means an Atom version, not a separate Revision entity.

