---
atom_family: SPEC
atom_id: AN-S-470
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 28
  updated_at: "2026-11-25T22:55:46.041960+00:00"
---
## Summary

Configure the Artifact timestamp timezone

## Claim

### Prose Claim


the Artifact timestamp timezone setting in Project Settings.


the Project Settings **may** set `[artifact_timestamps].timezone` **to** `local`, `UTC`, **or** an IANA timezone name, with `local` as the default; **every** emitted `updated_at` value uses `YYYY-MM-DD HH:MM:SS +ZZZZ` with its explicit numeric UTC offset, **and** the setting supplies its timezone interpretation.
