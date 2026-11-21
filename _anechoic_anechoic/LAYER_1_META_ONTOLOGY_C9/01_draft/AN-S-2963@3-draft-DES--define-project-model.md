---
atom_family: SPEC
atom_id: AN-S-2963
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: draft
  version: 3
  updated_at: 2026-10-28 16:27:23 +0400
---
## Summary

Define Project Model

## Scope

Project Model in the Subject model.

## Claim

### Prose Claim

Project Model **means** the vocabulary grouping that **groups** Subjects for what exists in a project: its Atoms, governing configurations, Scope Units, Actors, history, Projections, Selections, Implementation and actual execution contexts.

## Semantics

It covers Implementation as well as CAPRMEDO Atoms. It groups the vocabulary for project things; it is not another copy of those things, a folder, repository snapshot or Carrier. Subjects may name actual things or descriptions. A runtime occurrence and a record of it remain different things.

Project Model membership is displayed as `Project Model::Actor`. This is organizational membership, not structural containment (`>`) or broader-to-narrower classification (`/`). Membership supplies no property inheritance and does not create another canonical Subject target. `Actor/AI Agent` and `Actor/Operator` remain actual specializations with applicable Actor-property inheritance.

### Existing-target reference marker

Organizational membership may refer to an existing kind with `::@`; it does not declare another copy of that kind. The `@` modifier and its identity constraints are defined by the common Subject grammar. This does not itself settle whether an independent structural option has been declared.
