---
atom_family: SPEC
atom_id: AN-S-3693
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 25
  updated_at: 2026-10-26 06:05:43 +0400
---
## Summary

Define Claim

# Summary

Define Claim

## Scope

The logical Claims of Requirement, Method, Evaluation, and Delivery Atoms.

## Claim

A Claim **means** one independently replaceable statement owned by exactly
one RMED Atom. It governs Atom broadly, rather than Atom.Content, because
Claim representation varies. Every RMED Atom has one logical Claim, but Claim
has no universal representation carrier. A natural-language Claim uses
`atom.content.claim`. A fully formal Claim uses `atom.claim.*` or Governing
Configuration. Claim is not a generic Substance property required of every
Content Role.

## Semantics

A Requirement Claim specifies the required outcome; a Method Claim specifies
how it is achieved; an Evaluation Claim specifies a check and its expected
result; a Delivery Claim specifies delivery or representation. A formal Graph
Rule carries its fully formal Claim in its operative YAML `claim.*` mapping,
rather than in `atom.content.claim`. P uses Objective, O Operation, C
Concern, and A Question/Analysis under their own content contracts. The common
word Claim does not create a separate definition layer or require every Atom
to carry the same primary content label.

## Details
