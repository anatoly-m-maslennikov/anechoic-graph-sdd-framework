---
identity:
  atom_id: AN-S-270
context:
  container:
    component: C16
  tier: 2
  lens: QA
state:
  status: active
  version: 25
  updated_at: 2026-10-27 19:59:34 +0400
---
## Summary

Verify manage installed Extensions

# Verify manage installed Extensions

## Claim checked

CA-O-042 applies one exact Extension lifecycle transition atomically **and** reports its resulting installed state, **or** restores the prior state completely.

## Applicable when

apply whenever exact Extension source **or** version resolution, installed-state planning, lifecycle effects, **or** rollback handling changes.

## Test case

use one bounded Extension lifecycle trace: install an exact package into an empty inventory, update it **to** a second exact source **and** version, downgrade it **to** the first exact source **and** version, uninstall it, **then** attempt one transition containing a deliberately failing file effect.

## Acceptance criteria

install, update, downgrade, **and** uninstall **every** produce exactly the planned identity, source, version, file inventory, **and** verification status. the failing transition restores the complete prior installed state **and** reports rollback evidence.

## Failure disposition

reject the realization **and** preserve initial inventory, transition plan, source **and** version resolution, final inventories, failed effect, **and** rollback evidence.

## Post-effect failure coverage

execute the failing transition from a recorded prior installed state. inject its fault **after** **`>=1`** planned file **or** installed-state effect is applied **and** **before** final verification succeeds. for a single atomic publication, inject **after** publication; a rejected plan **or** unavailable package **before** apply does **not** prove rollback.

- compare the complete prior **and** restored installed state: exact identity, source, version, selected inventory, **and** owned Carrier bytes.
- verify that the failed transition leaves no partially selected Extension **or** unplanned file effect, reports failure rather than successful installation, **and** preserves actual recovery evidence.
- preserve unrelated Carriers **and** accepted Journal history. immutable evidence of the attempted transition is **not** installed-state residue **to** erase.
- fail the Evaluation **if** restoration is incomplete, unverified, **or** reported as complete solely because the failing effect itself was rejected.
