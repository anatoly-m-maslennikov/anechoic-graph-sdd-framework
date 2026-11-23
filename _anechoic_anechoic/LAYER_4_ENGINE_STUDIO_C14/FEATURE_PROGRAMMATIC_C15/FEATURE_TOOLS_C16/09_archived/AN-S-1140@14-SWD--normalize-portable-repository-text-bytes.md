---
atom_family: SPEC
atom_id: AN-S-1140
container:
  component: C16
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 12:35:51 +0400
---
## Summary

Normalize portable repository text bytes

# Normalize portable repository text bytes

## Applicable when

use this Method **when** governed repository text **must** have stable bytes across supported operating systems **and** tools.

## Procedure

1. read the repository-owned normalization policy **and** resolve the selected tracked text files **without** using host defaults as authority.
2. detect encoding, byte-order marks, line endings, final-newline state, **and** disallowed control bytes.
3. produce an exact dry-run of byte changes using the canonical encoding **and** newline rules.
4. on authorized apply, rewrite **only** files whose bytes differ **and** preserve **all** semantic text.
5. re-read **every** changed file **and** prove that a second normalization pass is byte-idempotent.

## Outcome

selected repository text has one policy-derived portable byte representation **and** remains unchanged on repeated normalization.

## Failure or stop

stop on undecodable input, an unsupported file class, missing policy, **or** a transformation that would change semantic text.
