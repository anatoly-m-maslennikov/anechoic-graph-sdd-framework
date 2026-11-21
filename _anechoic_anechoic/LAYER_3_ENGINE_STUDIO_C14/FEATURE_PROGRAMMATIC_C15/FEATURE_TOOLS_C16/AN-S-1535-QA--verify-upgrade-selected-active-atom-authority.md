---
atom_family: SPEC
atom_id: AN-S-1535
container:
  component: C16
tier: 1
context:
  lens: QA
state:
  status: active
  version: 26
  updated_at: 2026-10-27 19:59:32 +0400
---
## Summary

Verify upgrade selected active atom authority

# Verify upgrade selected active atom authority

## Claim checked

CA-O-045 upgrades one active Atom **or** a frozen bulk set **to** a strictly higher enabled `core` **or** `standard` Tier while preserving stable identity.

## Applicable when

apply **to** **any** realization of CA-O-045 **before** it can change an active Atom's Tier **or** authority location.

## Test case

use one fixture with one active standard-tier Atom selected singly **and** two active standard-tier Atoms selected as a frozen bulk set. record dry-runs for a same-tier target, a forbidden non-`core`/`standard` target, a disabled `core` target, **and** enabled higher `core` targets **in** the same Scope Unit **and** an explicit ancestor Scope Unit; attempt `--apply` **without** delegated authority, **then** apply the valid singular **and** bulk requests through sealed Initiative envelopes.

## Acceptance criteria

the unauthorized, same-Tier, forbidden-tier, **and** disabled-tier requests change no carrier; valid singular **and** bulk requests create one canonical higher-Tier carrier per source **in** the approved Scope Units, preserve **every** stable Atom ID, advance **every** revision exactly once, derive the ancestor filename scope segment **where** applicable, remove **every** former carrier, **and** leave no second active owner of **any** ID.

## Failure disposition

reject the realization **and** preserve Tier **and** ancestry evidence, dry-run maps, authority result, identity scans, revisions, **and** **any** duplicate **or** stale authority carrier.

## Post-effect failure coverage

from an independent recorded before-state, inject a failure **after** **`>=1`** selected Carrier is published at its target authority location **and** **before** the complete singular **or** bulk upgrade succeeds. also test a failed post-write verification from a separate baseline.

- verify restoration of **every** selected source **and** destination, with exact prior Carrier bytes, identity, Revision metadata, authority Relations, **and** path existence. preserve unrelated Carriers, pre-existing history, **and** immutable accepted Journal Records of actual effects.
- verify that no duplicate active identity **or** partial higher-authority set remains. an incomplete **or** unverified restoration fails the rollback guarantee.
- retain actual failure **and** recovery evidence. rejected preflight alone does **not** prove post-effect recovery; a failed apply is **not** reported as a successful upgrade.
