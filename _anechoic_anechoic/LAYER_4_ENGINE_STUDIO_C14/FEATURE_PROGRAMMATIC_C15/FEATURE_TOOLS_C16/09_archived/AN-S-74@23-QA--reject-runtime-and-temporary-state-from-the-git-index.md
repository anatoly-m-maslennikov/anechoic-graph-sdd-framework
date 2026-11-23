---
atom_family: SPEC
atom_id: AN-S-74
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 23
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Reject runtime and temporary state from the Git index

# Reject runtime and temporary state from the Git index

## Claim checked

Repository-local runtime, temporary, **and** Git-internal state cannot enter a commit through the managed pre-commit boundary.

## Test case

**in** separate runs, force-stage one file below `.anechoic_runtime` **and** one file below `.anechoic_tmp`, **then** invoke `git-hook pre-commit`.

## Acceptance criteria

Each run returns one stable local-machine-path diagnostic **before** commit creation **and** leaves the staged Carrier, working tree, index, refs, Journal, governed source, runtime, **and** temporary state byte-identical.

## Failure disposition

Reject the delivery **if** the boundary succeeds, silently unstages **or** rewrites either file, mutates governed state, **or** reports the runtime file as an Atom.
