---
atom_family: SPEC
atom_id: AN-S-2817
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 07:32:39 +0400
---
## Summary

Define Requirement Type Relation Definition

## Claim

Relation Definition is the Requirement Type defining a named reusable Relation Type: its canonical meaning, declared direction and applicable derived-inverse meaning. It remains distinct from an actual edge and from the Entity Definition describing Relation structure. It follows the required direct prose Claim and optional R Formal claim contract.

Its content.notation_for_subject property has zero or one string value carried in a fenced code block under ## Notation for subject. When the Relation Definition provides an admitted short Entity operator, that property is required and states its exact Entity notation. No dedicated shorthand is invented for Relation Types that use the general ((RELATION_TYPE)) form. Semantics or notation examples do not override the Claim's declared direct/derived meaning.

### Formal claim

```text
Atom/Content Role: Requirement/Type: Relation Definition.content.notation_for_subject[string]{0..1}
```

## Details

A1303 records the Type distinction. The required-if-short-notation condition stays in prose; advanced bracketed conditions are excluded. This Type Draft does not create a new Relation fact, register a syntax operator or promote a Current source.
