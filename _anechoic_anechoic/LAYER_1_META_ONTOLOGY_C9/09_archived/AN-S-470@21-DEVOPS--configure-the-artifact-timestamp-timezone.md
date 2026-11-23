---
atom_family: SPEC
atom_id: AN-S-470
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 21
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Configure the Artifact timestamp timezone

# Summary

Configure the Artifact timestamp timezone

## Scope

the Artifact timestamp timezone setting in Framework Instance Settings.

## Claim

the Framework Instance Settings Artifact **may** set `[artifact_timestamps].timezone` **to** `local`, `UTC`, **or** an IANA timezone name, with `local` as the default; **every** emitted `updated_at` value uses `YYYY-MM-DD HH:MM:SS +ZZZZ` with its explicit numeric UTC offset, **and** the setting supplies its timezone interpretation.

## Details
