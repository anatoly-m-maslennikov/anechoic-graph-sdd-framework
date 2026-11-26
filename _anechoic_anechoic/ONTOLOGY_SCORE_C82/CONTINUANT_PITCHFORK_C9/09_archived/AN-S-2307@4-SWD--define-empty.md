---
atom_family: SPEC
atom_id: AN-S-2307
container:
  component: C9
tier: 1
context:
  lens: SWD
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-25T23:14:19.798121+00:00"
---
## Summary

Define Empty

## Claim

### Prose Claim


The reusable lexical Term `Empty` for Workflow input values and ID routing.


Empty **means** an omitted input, null, **or** the empty string `""`. This Claim explicitly introduces the lexical Term instance named Empty at `Term//Empty`.

## Semantics

`undefined` denotes an omitted input value only; it does not add another supplied value to the admitted set. The literal string `"undefined"` is not Empty. A supplied null value and a supplied empty string `""` are Empty.

Whitespace-only strings, `0`, `false`, `[]`, and `{}` are not Empty. Do not trim, coerce, or apply a general truthiness test to extend this exact set. This definition does not establish programming-language-specific `None` semantics.

## Details

This Draft records the Operator-confirmed meaning and the initially flat lexical target under `Term`. The separate proposed Term branch and Method Type Term Definition declaration must be reconciled before adoption. It creates no Term groups, domain ID properties, Workflow definition, execution, or runtime implementation.

The role-only Draft marker allocates no canonical Method identity. Adoption requires the applicable source, Type, identity, naming, and lifecycle checks; this Draft supplies no evidence that those effects occurred. No dictionary Projection, extractor, or lookup service is required.

### Pending governing declarations

- [Entity root with the Term branch](../../04_requirement/draft/CA-R-1248@24-draft-CORE_META_MODEL-DEFINITION--define-entity.md).
- [Term kind and inherited structure](../../04_requirement/draft/CA-R-1318@30-draft-CORE_META_MODEL-DEFINITION--define-term.md).
- [Method Type Term Definition](../../04_requirement/draft/CA-R-draft-CORE_META_MODEL-ENTITY_DEFINITION--define-method-type-term-definition.md).
- [Dedicated Method meaning owner](../../04_requirement/draft/CA-R-1319@26-draft-CORE_META_MODEL--define-governed-term.md).

These links identify pending Draft dependencies, not Current admission.
