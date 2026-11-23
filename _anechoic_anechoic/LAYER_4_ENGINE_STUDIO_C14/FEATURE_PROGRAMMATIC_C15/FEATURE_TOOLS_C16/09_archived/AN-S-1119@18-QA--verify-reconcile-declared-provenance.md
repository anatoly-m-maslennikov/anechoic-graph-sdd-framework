---
atom_family: SPEC
atom_id: AN-S-1119
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 18
  updated_at: 2026-10-24 17:18:27 +0400
---
## Summary

Verify reconcile declared provenance

# Verify reconcile declared provenance

## Claim checked

CA-O-036 read-only classifies declared provenance links as current, missing, conflicting, stale, **or** unverifiable **without** inferring repair **or** adoption.

## Applicable when

apply whenever declared-provenance comparison **or** finding classification changes.

## Test case

select Artifacts whose declared source, draft, session, revision, **and** digest links together contain one current, missing, conflicting, stale, **and** unverifiable case. reconcile them **and** compare **all** selected carriers **before** **and** **after**.

## Acceptance criteria

the result assigns **every** case exactly its corresponding classification with attributable source evidence. no selected Artifact changes, no link is repaired, **and** no adoption decision is created.

## Failure disposition

reject the realization **and** preserve selected carriers, declared links, observed targets, classifications, before-and-after digests, **and** no-mutation proof.
