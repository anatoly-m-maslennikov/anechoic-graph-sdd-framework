---
atom_family: SPEC
atom_id: AN-S-3602
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 32
  updated_at: 2026-10-29 09:31:44 +0400
---
## Summary

Define Atom Subjects Graph

## Claim scope

Atom Subjects Graph Type values under Projection.

## Claim

Atom Subjects Graph **means** the Type value under Projection whose instances are non-authoritative ANECHOIC Graphs derived from selected current Atom Subjects, with Atom nodes linked by direct GOVERNS **and** DEPENDS_ON Subject Relations **to** their canonical Subject Target nodes. A Subject names the thing or topic an Atom governs or depends on; GOVERNS and DEPENDS_ON are the links from the Atom to that Subject, not the Subject itself. The Subject target is not an intermediate Subject object or a duplicated target definition.

## Details

**every** represented link retains the source Atom identity, exact Subject Path, canonical target identity, Relation Kind, direction, **and** source Atom ID and Version. its Relation Types and endpoint constraints remain governed by applicable Entity Definition constraints and other existing authority for their use; Relation Types use shared project-unique names and meanings, have no owning graph or Type Status, and this Projection Type does **not** create a mandatory per-Type admission record or default, nor an independently authored relation fact. represented targets retain their existing identities **without** an intermediate Subject object **or** duplicated target definitions.

an Atom Subjects Graph may represent canonical Subject Targets under one Subject-rooted hierarchy. this Projection Type remains the bipartite Atom-to-Subject link view; this specification does not claim that a particular renderer, tool, or existing Projection already supports that hierarchy.