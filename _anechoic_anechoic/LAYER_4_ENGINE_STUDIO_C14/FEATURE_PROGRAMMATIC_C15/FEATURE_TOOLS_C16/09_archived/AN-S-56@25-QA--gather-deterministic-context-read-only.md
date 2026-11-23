---
atom_family: SPEC
atom_id: AN-S-56
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 25
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Gather deterministic context read-only

# Gather deterministic context read-only

## Claim checked

COMMIT_CONTEXT gathers deterministic provisional context from **`=1`** durable trigger **without** mutating governed, runtime, **or** Git state under CA-R-804 **and** CA-M-087.

## Test case

prepare a fixed sealed trigger with a fixed Initiative, action identity, expected frontier, observation time, **and** repository fixture. snapshot **every** Atom, Projection, Journal, runtime output, index entry, **and** Git reference. invoke the Finder twice for equivalent inputs **and** once **after** changing **only** registered non-semantic transport metadata. capture its context **and** proposed message separately from effect receipts.

## Acceptance criteria

- equivalent contexts are byte-identical **after** excluding **only** the registered non-semantic transport metadata. a change **to** that metadata does **not** change context identity.
- the context includes the sealed Initiative, action identity, resolved target, expected **and** observed Revisions **or** digests, observed Git **and** Journal state, **and** revalidation inputs.
- the Finder **may** return the message Projection **and** provisional eligibility information admitted by CA-M-087. these are read-only descriptions, **not** a guaranteed future Commit, mutation authority, **or** a successful-effect receipt.
- no Git lease is acquired, Journal Record appended, runtime state written, path staged, **or** Commit created. **every** fixture snapshot remains unchanged.
- unresolved **or** nonconforming observed Project facts remain observable under CA-R-804; the Finder does **not** invent a conforming Atom identity **or** mutate the fixture **to** obtain deterministic output.

## Failure disposition

reject the Finder on missing **or** unstable required context, a mutation, an unregistered metadata exclusion, **or** a preview presented as mutation authority **or** completed work. retain the exact inputs, contexts, preview, **and** before/after snapshots.
