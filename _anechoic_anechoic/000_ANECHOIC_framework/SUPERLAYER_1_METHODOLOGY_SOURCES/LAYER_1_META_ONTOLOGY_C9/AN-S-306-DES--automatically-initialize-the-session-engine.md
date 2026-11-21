---
atom_family: SPEC
atom_id: AN-S-306
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: 2026-10-29 09:32:49 +0400
---
## Summary

Automatically initialize the session engine

## Claim

ANECHOIC **must** initialize its session engine at session start **and** **after** context compaction **without** requiring an operator command.

The session engine here means the Runtime responsible for the current Session and context, not a separately introduced model kind. C610 tracks its concrete Engine owner for later implementation.

## Details

Preserves the meaning of the legacy methodology Requirement ANECHOIC-METHODOLOGY-REQU-507-FRAMEWORK_METHODOLOGY-CORE-REQUIREMENT--automatically-initialize-the-session-engine. Its archived carrier retains the original header and provenance.
