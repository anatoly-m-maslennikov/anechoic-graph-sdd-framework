---
atom_family: SPEC
atom_id: AN-S-268
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Verify patch generic Artifact relations

# Verify patch generic Artifact relations

## Claim checked

CA-O-039 changes **only** valid direct relation targets **and** endpoint descriptors while preserving the source Artifact body **and** unrelated metadata.

## Applicable when

apply whenever generic relation-patch validation, canonical-reference resolution, **or** endpoint-descriptor handling changes.

## Test case

seal one source Artifact with known body digest **and** existing relations. submit one valid relative Scope Unit target with its endpoint descriptor together with one target that violates the registered relation direction; **then** submit **only** the valid relation change.

## Acceptance criteria

the mixed request changes nothing **and** identifies the invalid target. the valid request writes **only** the canonical direct target **and** endpoint descriptor, advances revision once, **and** preserves body digest **and** unrelated metadata.

## Failure disposition

reject the realization **and** preserve relation policy, source-owner context, requested targets, endpoint descriptors, dry-run, exact diff, revision, **and** body digest.

## Post-effect failure coverage

from an independent recorded before-state, inject a failure **after** a selected Relation **or** endpoint-descriptor write **and** **before** the complete transition is accepted.

- verify restoration of **every** selected mutable Carrier, metadata value, **and** canonical reference **to** the exact before-state, including the prior existence **or** absence of owned destination paths. unrelated Carriers remain unchanged.
- distinguish failed preflight, failed apply, successful restoration, **and** incomplete restoration. **none** is an accepted successful transition.
- retain evidence that the injected failure followed a real selected effect. preflight rejection alone does **not** prove recovery; incomplete **or** unverified restoration fails the rollback guarantee.
