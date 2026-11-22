---
atom_family: SPEC
atom_id: AN-S-249
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: active
  version: 23
  updated_at: 2026-10-27 19:59:30 +0400
---
## Summary

Record successor IDs while archiving predecessor

# Record successor IDs while archiving predecessor

## Claim checked

archiving a replaced predecessor records the explicit predecessor **and** already-active successor Atom IDs **only** **in** the authoritative Journal Event under CA-R-807. the Git Commit boundary follows CA-D-335.

## Test case

prepare an active predecessor at Version 4 **and** **`>=1`** distinct active successors at Version 1. include **`=1`** successor **and** **`>=2`** successors **in** separate fixtures. archive the predecessor under its unchanged Atom ID **and** Version, using the required @4.md archive suffix. seal the explicit predecessor ID **and** complete successor ID set **in** that Journal Event. exercise an individual approved change set **and** a larger approved atomic change set containing this archive effect.

## Acceptance criteria

- the predecessor's archived content **and** Version remain unchanged, **and** it has no active Carrier.
- its individual Journal Event records the Carrier transition **and** the complete explicit replacement IDs; current Atom Carriers contain no replacement history.
- **every** successor was active **before** predecessor archival; empty, duplicate, inactive, **or** self successor sets fail.
- the Git Commit **contains** **all** **and** **only** its approved atomic change set. predecessor **and** successor changes **may** share that Commit while retaining their individual Journal Events.
- no formal replacement relation **or** authoritative inverse history is invented.

## Failure disposition

reject missing **or** invalid replacement IDs, premature archival, lost historical content, a changed predecessor Version, an invalid archive filename, replacement history **in** an active Carrier, **or** an unapproved Commit boundary.
