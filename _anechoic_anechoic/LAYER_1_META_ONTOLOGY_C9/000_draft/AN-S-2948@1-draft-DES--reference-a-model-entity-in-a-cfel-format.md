---
atom_family: SPEC
atom_id: AN-S-2948
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-06 19:37:39 +0400
---
## Summary

Reference a Model entity in a CFEL Format

## Claim

### Prose Claim

`<x>` refers to the declared Model entity `x`. When used as `[<x>]`, it supplies the Format domain of existing instances of that entity, including its narrower kinds where applicable. It does not create a Model entity, an instance, or a literal value. Model Properties may supply such a domain when their instances are admitted.

A fixed Model Relation name such as `Relation//IS_CONTAINED_BY` is a Model reference and does not introduce a `$` participant. A typed participant such as `$a[<Atom>]` binds an existing instance. A Claim may relate that instance to a bare Model entity only when the applicable Relation Declaration admits those endpoint domains. For a declared kind `x`, `$a[<x>] ((INSTANCE_OF)) x` illustrates such a mixed instance-to-Model relation when its endpoints are admitted.

In `$container[<Workflow Run> OR <Step Run>]`, the alternatives define one union domain for one participant. A Relation count applies to the selected union as a whole, not separately to each alternative.

In a declaration-qualified expression call `<Kind>.p(a)`, `<Kind>` identifies the declaring Model kind.

The paired `<` and `>` around a Model reference mark that reference, including in a Format or a declaration expression call. Binary numeric `<` and `>` are comparisons governed by their respective CFEL Rules.

## Semantics

A Model reference identifies a declared Model entity.
