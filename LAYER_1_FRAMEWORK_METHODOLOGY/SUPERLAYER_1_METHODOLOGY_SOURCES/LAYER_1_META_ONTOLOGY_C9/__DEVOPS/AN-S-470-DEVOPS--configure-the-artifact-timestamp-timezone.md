---
atom_family: SPEC
atom_id: AN-S-470
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 28
  updated_at: 2026-11-04 09:30:21 +0400
---
## Summary

Configure the Artifact timestamp timezone

## Claim

### Prose Claim


the Artifact timestamp timezone setting in Project Settings.


the Project Settings **may** set `[artifact_timestamps].timezone` **to** `local`, `UTC`, **or** an IANA timezone name, with `local` as the default; **every** emitted `updated_at` value uses `YYYY-MM-DD HH:MM:SS +ZZZZ` with its explicit numeric UTC offset, **and** the setting supplies its timezone interpretation.
