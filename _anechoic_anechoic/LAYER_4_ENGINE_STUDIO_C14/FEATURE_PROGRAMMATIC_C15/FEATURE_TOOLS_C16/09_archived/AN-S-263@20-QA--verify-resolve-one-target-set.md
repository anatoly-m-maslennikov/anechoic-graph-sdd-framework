---
atom_family: SPEC
atom_id: AN-S-263
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 20
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Verify resolve one target set

# Verify resolve one target set

## Claim checked

CA-M-219 resolves one stable sealed target set from explicit identities **and** governed selectors **without** performing a check **or** mutation.

## Applicable when

apply whenever `TARGET_SET` identity resolution, ordering, sealing, **or** source-frontier handling changes.

## Test case

inspect the registered `TARGET_SET` unit **and** supply duplicate explicit identities **and** one governed selector that resolve **to** a known member set. resolve **and** seal the unchanged frontier. **in** a separate run, capture the expected source frontier, **then** change one selected source **after** capture but **before** completing that same sealing attempt. separately start a fresh request **after** the change has finished, **without** a precondition requiring the old frontier.

## Acceptance criteria

`TARGET_SET` has prefix `TARGET_SET`, immediate `TOOLS` owner, `unordered_unit` kind, Structural level `4`, address `102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/TARGET_SET`, **and** realization path `102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/TARGET_SET/`. the valid set **contains** **every** matching member once **in** stable order with its recorded source frontier **and** content digest; no target changes. the attempt whose captured frontier changed **before** completion returns no sealed accepted set. the fresh request **may** seal the new stable frontier **if** its selected sources **and** **all** other preconditions are valid; an earlier change alone does **not** make a fresh request stale.

## Failure disposition

reject the realization **and** preserve identities, selector, expected membership **and** order, sealed frontier **and** digest, stale-frontier result, **and** no-mutation evidence.
