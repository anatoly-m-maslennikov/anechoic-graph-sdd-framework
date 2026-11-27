---
atom_family: SPEC
atom_id: AN-S-2484
container:
  component: C18
tier: 4
context:
  lens: SWD
state:
  status: active
  version: 27
  updated_at: "2026-11-27T16:29:34.309627+00:00"
---
## Summary

Change one sealed target set

## Scope

use this Method **when** `BULK_CHANGE` **must** compose registered carrier operations over one sealed target set.

## Claim

### Prose Claim

1. Verify the BULK_CHANGE composition and executable binding under AN-S-2414 and AN-S-121.
2. resolve one sealed target set **and** declared registered create, structured patch, relation change, rename, move, lifecycle, **or** replacement operations.
3. derive a complete mutation-free change plan that identifies **every** explicit target, effect, precondition, collision and required reference rewrite. For Atom operations, bind independent one-Atom Actions and their own storage-effect safeguards; do not create a cross-Atom rollback boundary. Retain rollback actions only where separately governed for generic Artifact operations.
4. require explicit approval of the exact plan digest **and** recheck the target set frontier **and** **every** effect precondition **before** apply.
5. For Atom operations, execute only the unchanged approved one-Atom Actions. Validate each Action's current source and permission before its effect; verify and record its actual outcome. A valid no-op has no edit, Version, timestamp or archive effect and does not stop the sequence. Stop at the first failed Action, retain completed Actions and leave remaining targets untouched. Report the successful, no-op, failed, uncertain and untouched targets truthfully. For separately governed generic Artifact operations, retain the admitted transaction, effect verification and rollback evidence.

## Details

### Outcome

one explicitly approved unchanged `BULK_CHANGE` plan reports the actual outcomes of its explicit targets. Atom Actions remain independent; a several-Atom sequence has no cross-Atom all-or-nothing promise. Separately governed generic Artifact transactions retain their own outcome contract.

### Failure or stop

do **not** mutate **before** an approved complete plan. For Atom operations, stale source, failed precondition, unplanned effect, collision, failed verification or uncertain recording stops the sequence at that Action. Preserve that Action's applicable storage safeguards without reverting earlier completed Atom Actions or executing the remainder. Resume and retry policy is deferred. Separately governed generic Artifact operations retain their admitted stop or rollback behavior.
