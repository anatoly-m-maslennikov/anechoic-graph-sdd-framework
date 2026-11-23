---
atom_family: SPEC
atom_id: AN-S-279
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 10
  updated_at: 2026-10-23 03:18:40 +0400
---
## Summary

Rebuild one project graph state from configuration

# Rebuild one project graph state from configuration

## Claim checked

the graph-state Tool derives one current non-authoritative Projection from the inputs admitted by CA-M-149: authoritative Project Structure, separate Settings authority, **and** the selected Atom, directory-observation **and** Journal evidence frontier.

## Test case

rebuild graph state twice from unchanged source Revisions **and** observations. include accepted declarations whose folder materialization **or** Goal coverage is missing, **and** observed directories that do **not** match an accepted declaration.

## Acceptance criteria

- both Projections agree semantically **and** identify their selected sources.
- accepted Scope Unit declarations **and** concrete bindings come **only** from Project Structure. Project Settings **and** Framework Instance Settings retain their separate selected-value authority.
- declarations, Atom Claims, directory observations **and** Journal evidence remain distinct. missing coverage **and** mismatches stay visible **without** creating **or** rewriting accepted declarations.
- no direct output edit becomes authority, **and** **all** source Carriers remain unchanged.
- missing, invalid **or** incompletely read required authority is reported as incomplete coverage, **not** a complete accepted Project Structure.

## Failure disposition

reject the Projection as stale, nondeterministic, source-altering **or** authority-creating **when** **any** corresponding condition fails.
